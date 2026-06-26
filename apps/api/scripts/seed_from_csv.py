"""
Seed doctors from docter.csv (17k records from 30+ Indian cities).
Geocodes each unique CITY once via Nominatim, then inserts all doctors.
Usage: python scripts/seed_from_csv.py
"""
import asyncio
import csv
import os
import sys
import time
import uuid
from datetime import datetime, timezone
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CSV_PATH = r"C:\Users\ankur\Documents\projects\med\dataset\docter.csv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "TravelHealthFinderBot/1.0"
BATCH_SIZE = 200


async def geocode_city(session: aiohttp.ClientSession, city: str) -> tuple:
    """Return (lat, lng) for a city, or (None, None) on failure."""
    params = {"q": f"{city}, India", "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    try:
        async with session.get(NOMINATIM_URL, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  Geocode failed for {city}: {e}")
    return None, None


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Read CSV
    print("Reading docter.csv...")
    rows = []
    with open(CSV_PATH, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"Loaded {len(rows)} rows from CSV.")

    # Collect unique cities
    unique_cities = set(r.get("City", "").strip() for r in rows if r.get("City", "").strip())
    print(f"Unique cities: {len(unique_cities)} — geocoding...")

    city_coords = {}
    async with aiohttp.ClientSession() as http:
        for i, city in enumerate(sorted(unique_cities)):
            lat, lng = await geocode_city(http, city)
            city_coords[city] = (lat, lng)
            print(f"  [{i+1}/{len(unique_cities)}] {city} -> ({lat}, {lng})")
            time.sleep(1.1)  # Nominatim rate limit: 1 req/sec

    print("\nInserting doctors into database...")
    async with AsyncSessionLocal() as db:
        # Wipe existing data first
        await db.execute(text("DELETE FROM doctors"))
        await db.commit()
        print("  Cleared existing doctors table.")

        inserted = 0
        batch = []
        for row in rows:
            city = row.get("City", "").strip()
            lat, lng = city_coords.get(city, (None, None))
            name = row.get("Name", "").strip()
            if not name:
                continue

            # Parse consult fee — strip currency symbols / non-numeric cruft
            raw_fee = row.get("Consult Fee", "").strip()
            consult_fee = ""
            try:
                digits = "".join(filter(str.isdigit, raw_fee))
                if digits:
                    consult_fee = f"Rs. {digits}"
            except Exception:
                consult_fee = raw_fee

            speciality = row.get("Speciality", "").strip()
            degree = row.get("Degree", "").strip()
            location = row.get("Location", "").strip()
            dp_score = row.get("DP Score", "").strip()
            npv_value = row.get("NPV Value", "").strip()
            years_exp = row.get("Years of Experience", "0").strip()

            try:
                years_exp_int = int("".join(filter(str.isdigit, years_exp)) or "0")
            except Exception:
                years_exp_int = 0

            batch.append({
                "id": str(uuid.uuid4()),
                "name": name,
                "degree": degree[:500] if degree else None,
                "dp_score": dp_score[:50] if dp_score else None,
                "npv_value": npv_value[:100] if npv_value else None,
                "location": location[:500] if location else None,
                "city": city[:100] if city else None,
                "consult_fee": consult_fee[:100] if consult_fee else None,
                "years_of_experience": str(years_exp_int),
                "speciality": speciality[:500] if speciality else None,
                "latitude": lat,
                "longitude": lng,
                "created_at": datetime.now(timezone.utc),
            })

            if len(batch) >= BATCH_SIZE:
                await db.execute(
                    text("""
                        INSERT INTO doctors (id, name, degree, dp_score, npv_value, location, city, consult_fee, years_of_experience, speciality, latitude, longitude, created_at)
                        VALUES (:id, :name, :degree, :dp_score, :npv_value, :location, :city, :consult_fee, :years_of_experience, :speciality, :latitude, :longitude, :created_at)
                    """),
                    batch,
                )
                await db.commit()
                inserted += len(batch)
                print(f"  Inserted {inserted}/{len(rows)} doctors...")
                batch = []

        if batch:
            await db.execute(
                text("""
                    INSERT INTO doctors (id, name, degree, dp_score, npv_value, location, city, consult_fee, years_of_experience, speciality, latitude, longitude, created_at)
                    VALUES (:id, :name, :degree, :dp_score, :npv_value, :location, :city, :consult_fee, :years_of_experience, :speciality, :latitude, :longitude, :created_at)
                """),
                batch,
            )
            await db.commit()
            inserted += len(batch)

    print(f"\nDone! Inserted {inserted} doctors into Supabase.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
