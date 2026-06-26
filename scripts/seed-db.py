"""
Seed script: Populates city_configs and fee_estimates tables.
Run AFTER running alembic upgrade head.
Usage: python scripts/seed-db.py
"""
import sys, os, asyncio, json, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../apps/api"))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../apps/api/.env"))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://dev_user:dev_password@localhost:5432/travel_health")

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# ─── City Seed Data ───────────────────────────────────────
CITIES = [
    {"city_name": "Delhi",      "display_name": "New Delhi",   "latitude": 28.6139, "longitude": 77.2090, "search_radius": 5000},
    {"city_name": "Mumbai",     "display_name": "Mumbai",      "latitude": 19.0760, "longitude": 72.8777, "search_radius": 5000},
    {"city_name": "Bengaluru",  "display_name": "Bengaluru",   "latitude": 12.9716, "longitude": 77.5946, "search_radius": 5000},
    {"city_name": "Hyderabad",  "display_name": "Hyderabad",   "latitude": 17.3850, "longitude": 78.4867, "search_radius": 5000},
    {"city_name": "Chennai",    "display_name": "Chennai",     "latitude": 13.0827, "longitude": 80.2707, "search_radius": 5000},
    {"city_name": "Pune",       "display_name": "Pune",        "latitude": 18.5204, "longitude": 73.8567, "search_radius": 5000},
    {"city_name": "Jaipur",     "display_name": "Jaipur",      "latitude": 26.9124, "longitude": 75.7873, "search_radius": 5000},
    {"city_name": "Ahmedabad",  "display_name": "Ahmedabad",   "latitude": 23.0225, "longitude": 72.5714, "search_radius": 5000},
    {"city_name": "Kolkata",    "display_name": "Kolkata",     "latitude": 22.5726, "longitude": 88.3639, "search_radius": 5000},
    {"city_name": "Chandigarh", "display_name": "Chandigarh",  "latitude": 30.7333, "longitude": 76.7794, "search_radius": 4000},
    {"city_name": "Mohali",     "display_name": "Mohali",      "latitude": 30.7046, "longitude": 76.7179, "search_radius": 4000},
    {"city_name": "Lucknow",    "display_name": "Lucknow",     "latitude": 26.8467, "longitude": 80.9462, "search_radius": 5000},
    {"city_name": "Surat",      "display_name": "Surat",       "latitude": 21.1702, "longitude": 72.8311, "search_radius": 5000},
]


async def seed_cities(session: AsyncSession):
    from models import CityConfig
    for city_data in CITIES:
        existing = await session.execute(
            select(CityConfig).where(CityConfig.city_name == city_data["city_name"])
        )
        if not existing.scalar_one_or_none():
            session.add(CityConfig(**city_data))
    await session.commit()
    print(f"✓ Seeded {len(CITIES)} cities")


async def seed_fees(session: AsyncSession):
    from models import FeeEstimate
    # Run ETL script to get fee data
    script_path = os.path.join(os.path.dirname(__file__), "parse-fee-dataset.py")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠ Fee ETL failed: {result.stderr}. Skipping fee seed.")
        return

    try:
        fees = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("⚠ Could not parse fee ETL output. Skipping fee seed.")
        return

    inserted = 0
    for fee_data in fees:
        existing = await session.execute(
            select(FeeEstimate).where(
                FeeEstimate.city == fee_data["city"],
                FeeEstimate.specialist_type == fee_data["specialist_type"],
            )
        )
        if not existing.scalar_one_or_none():
            session.add(FeeEstimate(**fee_data))
            inserted += 1

    await session.commit()
    print(f"✓ Seeded {inserted} fee estimates from docter.csv")


async def main():
    async with SessionLocal() as session:
        print("Seeding database...")
        await seed_cities(session)
        await seed_fees(session)
        print("✓ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
