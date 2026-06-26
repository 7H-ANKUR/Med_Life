"""
Local DB & OpenStreetMap (Nominatim) location service.
Replaces Google Maps API calls.
"""
import math
import aiohttp
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, String, cast
from models import Doctor

# ─── Specialist → Search Keyword Mapping ──────────────────
# This mapping helps translate standard search queries to our DB specialities
SPECIALIST_KEYWORDS = {
    "Cardiologist": ["Cardiologist", "Heart"],
    "Dermatologist": ["Dermatologist", "Skin"],
    "Orthopedic Surgeon": ["Orthopedic"],
    "Gynecologist": ["Gynecologist", "Obstetrician"],
    "Pediatrician": ["Pediatrician", "Children"],
    "General Physician": ["General Physician", "Internal Medicine"],
    "Dentist": ["Dentist", "Endodontist", "Orthodontist", "Periodontist"],
    "Ophthalmologist": ["Ophthalmologist", "Eye"],
    "Neurologist": ["Neurologist", "Brain"],
    "Gastroenterologist": ["Gastroenterologist", "GastroIntestinal"],
    "ENT Specialist": ["ENT", "Otorhinolaryngologist"],
    "Psychiatrist": ["Psychiatrist", "Mental"],
    "Physiotherapist": ["Physiotherapist", "Rehabilitation"],
    "Nephrologist": ["Nephrologist", "Renal"],
    "Endocrinologist": ["Endocrinologist", "Diabetes"],
    "Urologist": ["Urologist", "Urology"],
    "Emergency Physician": ["Emergency", "Trauma"],
}

class LocationService:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "TravelHealthFinderBot/1.0"

    async def nearby_search(
        self,
        db: AsyncSession,
        lat: float,
        lng: float,
        specialist_type: str | None = None,
        place_type: str = "all",
        radius: int = 5000,
        emergency: bool = False,
        city: str | None = None,
    ) -> list[dict]:
        """
        Fetch nearby doctors/hospitals from local Supabase DB.
        Strategy:
        1. If city is provided, filter by city name first (most reliable).
        2. Then filter by specialist type.
        3. Fall back to distance-based search with a wide radius.
        """
        stmt = select(Doctor)

        # Always filter by city name when provided — city-name match is
        # far more reliable than GPS radius for our dataset
        if city:
            stmt = stmt.where(Doctor.city.ilike(f"%{city.strip()}%"))

        # Filter by specialist type
        if specialist_type:
            keywords = SPECIALIST_KEYWORDS.get(specialist_type, [specialist_type])
            conditions = [Doctor.speciality.ilike(f"%{k}%") for k in keywords]
            stmt = stmt.where(or_(*conditions))

        result = await db.execute(stmt)
        doctors = result.scalars().all()

        places = []
        for d in doctors:
            # Compute distance if we have GPS coords, otherwise set 0 for city-matched results
            dist = 0
            if d.latitude is not None and d.longitude is not None:
                dist = int(self._haversine(lat, lng, d.latitude, d.longitude))

            places.append({
                "place_id": d.id,
                "name": d.name,
                "vicinity": f"{d.location}, {d.city}",
                "rating": self._parse_dp_score(d.dp_score),
                "user_ratings_total": self._parse_npv_value(d.npv_value),
                "_distance_meters": dist,
                "_place_type": "clinic" if any(k in (d.speciality or "") for k in ["Physician", "General", "Clinic"]) else "hospital",
                "_doctor_fee": d.consult_fee,
                "_doctor_exp": d.years_of_experience,
                "_doctor_degree": d.degree,
                "_doctor_speciality": d.speciality,
                "geometry": {"location": {"lat": d.latitude or lat, "lng": d.longitude or lng}}
            })

        # Sort by distance (0-distance city-matched results come first, then by proximity)
        places.sort(key=lambda x: x["_distance_meters"])
        return places


    async def place_detail(self, db: AsyncSession, place_id: str) -> dict:
        """Fetch full doctor/place details from local DB."""
        stmt = select(Doctor).where(cast(Doctor.id, String) == place_id)
        result = await db.execute(stmt)
        doctor = result.scalar_one_or_none()
        
        if not doctor:
            return {}
            
        return {
            "place_id": doctor.id,
            "name": doctor.name,
            "formatted_address": f"{doctor.location}, {doctor.city}",
            "formatted_phone_number": "Contact Clinic directly",
            "rating": self._parse_dp_score(doctor.dp_score),
            "user_ratings_total": self._parse_npv_value(doctor.npv_value),
            "geometry": {"location": {"lat": doctor.latitude, "lng": doctor.longitude}},
            "speciality": doctor.speciality,
            "degree": doctor.degree,
            "consult_fee": doctor.consult_fee,
            "years_of_experience": doctor.years_of_experience,
            "city": doctor.city
        }

    async def geocode_city(self, city_name: str) -> tuple[float | None, float | None]:
        """Convert city name → (lat, lng) using Nominatim."""
        params = {"q": f"{city_name}, India", "format": "json", "limit": 1}
        headers = {"User-Agent": self.user_agent}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.nominatim_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            print(f"Nominatim geocode failed: {e}")
        return None, None

    def build_navigate_url(self, lat: float, lng: float) -> str:
        """Build a Google Maps navigation deeplink using lat/lng (since OSM place_id won't work in Google Maps)."""
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&travelmode=driving"

    # ─── Helpers ──────────────────────────────────────────
    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Compute distance in meters between two lat/lng points."""
        R = 6_371_000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a))
        
    @staticmethod
    def _parse_dp_score(score: str | None) -> float:
        """Parse '98%' into a 4.9 float rating."""
        if not score or not score.endswith('%'):
            return 4.0 # Default fallback
        try:
            val = float(score.strip('%'))
            return round((val / 100) * 5.0, 1)
        except ValueError:
            return 4.0
            
    @staticmethod
    def _parse_npv_value(npv: str | None) -> int:
        """Parse '(30 patients)' into an integer 30."""
        if not npv:
            return 0
        try:
            return int(''.join(filter(str.isdigit, npv)))
        except ValueError:
            return 0

    @staticmethod
    def format_distance(meters: int) -> str:
        if meters < 1000:
            return f"{meters} m"
        return f"{meters / 1000:.1f} km"

location_service = LocationService()
