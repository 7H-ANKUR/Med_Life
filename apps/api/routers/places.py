"""
Places router — the most critical router.
Proxies local DB calls, applies the ranking engine, and enriches results with
live Apify Google Maps photos fetched in parallel.
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

from database import get_db
from schemas.places import NearbyResponse, PlaceResult, FeeRange, LocationPoint, RouteResponse
from services.location_service import location_service
from services.ranking_service import rank_places
from services.fee_service import get_fee_range, NATIONAL_FALLBACK
from services.apify_service import apify_service
from config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _shape_result(place: dict, fee_data: dict | None, photo_url: str | None = None) -> PlaceResult:
    """Convert local Doctor dict → PlaceResult schema."""
    loc = place.get("geometry", {}).get("location", {})
    meters = place.get("_distance_meters")

    return PlaceResult(
        place_id=str(place.get("place_id", "")),
        name=place.get("name", ""),
        place_type=place.get("_place_type", "clinic"),
        address=place.get("vicinity"),
        phone=place.get("formatted_phone_number"),
        rating=place.get("rating"),
        review_count=place.get("user_ratings_total"),
        open_now=place.get("opening_hours", {}).get("open_now", True),
        distance_meters=meters,
        distance_label=location_service.format_distance(meters) if meters else None,
        fee_estimate=FeeRange(**{k: fee_data[k] for k in ("min", "max", "currency")}) if fee_data else None,
        score=place.get("_score"),
        emergency_capable=place.get("_place_type") == "hospital",
        location=LocationPoint(lat=loc.get("lat", 0), lng=loc.get("lng", 0)) if loc else None,
        maps_url=(
            f"https://www.google.com/maps/search/?api=1&query={loc.get('lat', 0)},{loc.get('lng', 0)}"
            if loc else None
        ),
        photo_url=photo_url,  # enriched from Apify batch fetch
        speciality=place.get("_doctor_speciality"),
    )


@router.get("/nearby", response_model=NearbyResponse)
@limiter.limit(settings.rate_limit_places)
async def nearby(
    request: Request,
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    city: Optional[str] = Query(None),
    specialist_type: Optional[str] = Query(None),
    place_type: str = Query("all"),
    emergency: bool = Query(False),
    open_now: Optional[bool] = Query(None),
    budget_max: Optional[int] = Query(None),
    radius: int = Query(5000, ge=500, le=50000),
    rating_min: Optional[float] = Query(None, ge=1.0, le=5.0),
    language: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Resolve location ──────────────────────────────────────────────
    if not lat or not lng:
        if city:
            lat, lng = await location_service.geocode_city(city)
            if not lat:
                raise HTTPException(400, f"Could not geocode city: {city}")
        else:
            raise HTTPException(400, "Either lat/lng or city must be provided")

    # ── 2. Local DB Search ───────────────────────────────────────────────
    try:
        raw_places = await location_service.nearby_search(
            db=db,
            lat=lat, lng=lng,
            specialist_type=specialist_type,
            place_type=place_type,
            radius=radius,
            emergency=emergency,
            city=city,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    if not raw_places:
        # Retry without city filter (GPS-only fallback with big radius)
        try:
            raw_places = await location_service.nearby_search(
                db, lat, lng, specialist_type, place_type, radius=50000, emergency=emergency
            )
        except Exception:
            pass

    # ── 3. Attach fee estimates ──────────────────────────────────────────
    fee_data = None
    if specialist_type:
        fee_data = await get_fee_range(specialist_type, city, db)
    else:
        fee_data = {"min": 300, "max": 1500, "currency": "INR"}

    for p in raw_places:
        p["_fee_min"] = fee_data.get("min", 0)
        p["_fee_max"] = fee_data.get("max", 1500)
        if p.get("_doctor_fee"):
            try:
                val = int("".join(filter(str.isdigit, p["_doctor_fee"])))
                if val:
                    p["_fee_min"] = val
                    p["_fee_max"] = val
            except Exception:
                pass

    # ── 4. Rank results ──────────────────────────────────────────────────
    context = {
        "mode": "emergency" if emergency else "normal",
        "specialist_type": specialist_type,
        "language_pref": language,
        "open_now_required": open_now is True,
        "budget_max": budget_max,
        "rating_min": rating_min,
        "is_24x7_required": False,
    }
    ranked = rank_places(raw_places, context)[:limit]

    # ── 5. Batch-fetch photos from Apify in parallel ──────────────────────
    # We fetch photos concurrently for ALL ranked results (capped at `limit`).
    # Each individual call has a 45-second timeout; failures return None (graceful).
    photo_map: dict[str, str | None] = {}
    if ranked and city:
        try:
            print(f"[Places] Fetching Apify photos for {len(ranked)} places in '{city}'...")
            photo_map = await asyncio.wait_for(
                apify_service.fetch_photos_batch(ranked, city),
                timeout=60.0,  # max 60 s for the whole batch
            )
            print(f"[Places] Apify photo fetch complete. Got {sum(1 for v in photo_map.values() if v)} photos.")
        except asyncio.TimeoutError:
            print("[Places] Apify batch photo fetch timed out. Proceeding without photos.")
        except Exception as e:
            print(f"[Places] Apify batch photo fetch error: {e}. Proceeding without photos.")

    # ── 6. Shape final results ───────────────────────────────────────────
    results = [
        _shape_result(p, fee_data, photo_map.get(p.get("name", "")))
        for p in ranked
    ]

    return NearbyResponse(
        results=results,
        total=len(results),
        radius_used=radius,
        emergency_mode=emergency,
        city=city,
    )


@router.get("/route", response_model=RouteResponse)
async def route(
    to_place_id: str = Query(...),
    from_lat: Optional[float] = Query(None),
    from_lng: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    detail = await location_service.place_detail(db, to_place_id)
    if not detail or "geometry" not in detail:
        raise HTTPException(404, "Place coordinates not found")

    lat = detail["geometry"]["location"]["lat"]
    lng = detail["geometry"]["location"]["lng"]
    deeplink = location_service.build_navigate_url(lat, lng)
    return RouteResponse(maps_deeplink=deeplink)


@router.get("/{place_id}")
async def place_detail(place_id: str, db: AsyncSession = Depends(get_db)):
    try:
        detail = await location_service.place_detail(db, place_id)
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    if not detail:
        raise HTTPException(404, "Place not found")

    # Full Apify scrape is too slow (30s+), so we bypass it for instant loading.
    # We rely purely on Google Places API details.
    apify_data = {}
    # apify_data = await apify_service.fetch_place_details(
    #     place_name=detail.get("name"),
    #     city=detail.get("city", ""),
    # )

    # Normalize photo URLs
    photo_urls: list[str] = []
    raw_photos = apify_data.get("photos", [])
    for img in raw_photos[:3]:
        if isinstance(img, dict):
            url = img.get("imageUrl") or img.get("url")
            if url:
                photo_urls.append(url)
        elif isinstance(img, str):
            photo_urls.append(img)

    phone = apify_data.get("phone") or detail.get("formatted_phone_number")
    website = apify_data.get("website")
    live_rating = apify_data.get("rating") or detail.get("rating")
    live_reviews = apify_data.get("review_count") or detail.get("user_ratings_total")

    loc = detail.get("geometry", {}).get("location", {})
    return {
        "place_id": place_id,
        "name": detail.get("name"),
        "address": detail.get("formatted_address"),
        "phone": phone,
        "website": website,
        "rating": live_rating,
        "review_count": live_reviews,
        "open_now": True,
        "hours": [],
        "photos": photo_urls,
        "reviews": apify_data.get("reviews", [])[:5],
        "location": loc,
        "maps_url": (
            f"https://www.google.com/maps/search/?api=1&query={loc.get('lat', 0)},{loc.get('lng', 0)}"
            if loc else None
        ),
        "speciality": detail.get("speciality"),
        "degree": detail.get("degree"),
        "consult_fee": detail.get("consult_fee"),
        "years_of_experience": detail.get("years_of_experience"),
    }
