import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from config import settings

# Google Maps Scraper actor on Apify
ACTOR_ID = "compass~crawler-google-places"

# Direct Apify REST endpoint for running actors (avoids SDK version issues)
APIFY_BASE_URL = "https://api.apify.com/v2"


class ApifyService:
    def __init__(self):
        self.api_key = settings.apify_api_key
        self.actor_id = ACTOR_ID

    # ─── Batch photo fetch for the list view ──────────────────────────────
    async def fetch_photos_batch(
        self, places: list[dict], city: str
    ) -> dict[str, str | None]:
        """
        Fetch the FIRST photo for each place in parallel using the
        Apify Google Maps Scraper REST API.
        Returns a dict: { place_name → photo_url | None }
        """
        if not self.api_key:
            return {}

        tasks = [
            self._fetch_single_photo(p.get("name", ""), city)
            for p in places
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        photo_map: dict[str, str | None] = {}
        for p, result in zip(places, results):
            name = p.get("name", "")
            if isinstance(result, Exception) or not result:
                photo_map[name] = None
            else:
                photo_map[name] = result
        return photo_map

    async def _fetch_single_photo(self, place_name: str, city: str) -> str | None:
        """
        Use Apify's synchronous task endpoint to quickly get 1 photo for a place.
        Uses maxCrawledPlacesPerSearch=1 and maxImages=1 for speed.
        """
        if not place_name:
            return None

        query = f"{place_name} {city} clinic hospital"
        run_input = {
            "searchStringsArray": [query],
            "maxCrawledPlacesPerSearch": 1,
            "maxImages": 1,
            "maxReviews": 0,
            "language": "en",
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Use the synchronous run endpoint (waits for completion)
                url = f"{APIFY_BASE_URL}/acts/{self.actor_id}/run-sync-get-dataset-items"
                async with session.post(
                    url,
                    json=run_input,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=45),
                    params={"token": self.api_key},
                ) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    if not data or not isinstance(data, list):
                        return None
                    place = data[0]
                    # Try multiple photo field formats
                    image_urls = place.get("imageUrls", [])
                    if image_urls:
                        if isinstance(image_urls[0], dict):
                            return image_urls[0].get("imageUrl")
                        if isinstance(image_urls[0], str):
                            return image_urls[0]
                    # Some actors return photos field
                    photos = place.get("photos", [])
                    if photos:
                        if isinstance(photos[0], dict):
                            return photos[0].get("url") or photos[0].get("imageUrl")
                        if isinstance(photos[0], str):
                            return photos[0]
                    return None
        except Exception as e:
            print(f"[Apify] Photo fetch failed for '{place_name}': {e}")
            return None

    # ─── Full detail fetch (used for individual place detail page) ─────────
    async def fetch_place_details(self, place_name: str, city: str) -> Dict[str, Any]:
        """
        Scrape Google Maps for photos, phone number, rating, reviews and website
        for a single place. Used on the place detail endpoint.
        """
        if not self.api_key:
            print("[Apify] API key is missing. Skipping scrape.")
            return {}

        query = f"{place_name} {city} hospital clinic"
        run_input = {
            "searchStringsArray": [query],
            "maxCrawledPlacesPerSearch": 1,
            "language": "en",
            "maxImages": 5,
            "maxReviews": 5,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            print(f"[Apify] Fetching details for: {query}")
            async with aiohttp.ClientSession() as session:
                url = f"{APIFY_BASE_URL}/acts/{self.actor_id}/run-sync-get-dataset-items"
                async with session.post(
                    url,
                    json=run_input,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                    params={"token": self.api_key},
                ) as resp:
                    if resp.status != 200:
                        print(f"[Apify] HTTP {resp.status} for {place_name}")
                        return {}
                    data = await resp.json()
                    if not data or not isinstance(data, list):
                        return {}

                    place = data[0]

                    # Extract photos
                    photos = []
                    image_urls = place.get("imageUrls", [])
                    if image_urls:
                        for img in image_urls[:5]:
                            if isinstance(img, dict):
                                url_val = img.get("imageUrl") or img.get("url")
                                if url_val:
                                    photos.append(url_val)
                            elif isinstance(img, str):
                                photos.append(img)

                    # Fallback photos field
                    if not photos:
                        for img in place.get("photos", [])[:5]:
                            if isinstance(img, dict):
                                url_val = img.get("url") or img.get("imageUrl")
                                if url_val:
                                    photos.append(url_val)
                            elif isinstance(img, str):
                                photos.append(img)

                    result = {
                        "phone": place.get("phone") or place.get("phoneUnformatted"),
                        "website": place.get("website"),
                        "photos": photos,
                        "reviews": place.get("reviews", [])[:5],
                        "rating": place.get("totalScore"),
                        "review_count": place.get("reviewsCount"),
                        "address": place.get("address"),
                        "maps_url": place.get("url"),
                        "location": place.get("location"),
                    }
                    print(f"[Apify] Success for {place_name}: {len(photos)} photos")
                    return result

        except Exception as e:
            print(f"[Apify] Detail fetch failed for '{place_name}': {e}")
            return {}


apify_service = ApifyService()
