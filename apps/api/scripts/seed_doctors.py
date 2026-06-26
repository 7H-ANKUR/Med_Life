import os
import sys
import json
import asyncio
import argparse
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Doctor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment.")
    exit(1)

# Initialize SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "TravelHealthFinderBot/1.0"

async def geocode_location(session: aiohttp.ClientSession, location: str, city: str):
    """Geocode using Nominatim API."""
    query = f"{location}, {city}, India"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": USER_AGENT}
    
    try:
        async with session.get(NOMINATIM_URL, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Geocoding error for {query}: {e}")
        
    return None, None

async def process_batch(db_session, http_session, batch):
    """Process a batch of doctors, geocode them, and save to DB."""
    tasks = []
    for doc in batch:
        loc = doc.get("Location", "")
        city = doc.get("City", "")
        # Rate limit Nominatim (strictly 1 req/sec)
        tasks.append(geocode_location(http_session, loc, city))
        
    # Wait for geocoding sequentially to respect Nominatim limits
    coords = []
    for t in tasks:
        coords.append(await t)
        await asyncio.sleep(1.2) # Sleep to respect 1 req/sec limit
        
    # Prepare DB models
    new_doctors = []
    for doc, (lat, lon) in zip(batch, coords):
        # We need to skip duplicate names or handle it
        d = Doctor(
            name=doc.get("Name", "Unknown"),
            degree=doc.get("Degree"),
            dp_score=doc.get("DP Score"),
            npv_value=doc.get("NPV Value"),
            location=doc.get("Location"),
            city=doc.get("City"),
            consult_fee=doc.get("Consult Fee"),
            years_of_experience=doc.get("Years of Experience"),
            speciality=doc.get("Speciality"),
            latitude=lat,
            longitude=lon
        )
        db_session.add(d)
    
    await db_session.commit()

async def main(limit=None):
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "dataset", "doctor.json")
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at {dataset_path}")
        return

    print("Loading dataset...")
    doctors = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                doctors.append(json.loads(line))
                
    if limit:
        doctors = doctors[:limit]
        print(f"Limiting to {limit} records for testing...")

    print(f"Loaded {len(doctors)} doctors. Starting ingestion and geocoding...")
    
    async with async_session() as db_session:
        async with aiohttp.ClientSession() as http_session:
            batch_size = 10
            for i in range(0, len(doctors), batch_size):
                batch = doctors[i:i+batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(doctors)+batch_size-1)//batch_size}...")
                await process_batch(db_session, http_session, batch)
                
    print("✅ Ingestion complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed doctors into Supabase")
    parser.add_argument("--limit", type=int, help="Limit the number of records to process")
    args = parser.parse_args()
    
    asyncio.run(main(limit=args.limit))
