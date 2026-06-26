import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    print("❌ GOOGLE_MAPS_API_KEY not found")
    exit()

print("=" * 60)
print("GOOGLE MAPS API TEST SUITE")
print("=" * 60)

# --------------------------------------------------
# 1. GEOCODING API
# --------------------------------------------------
print("\n[1] Testing Geocoding API")

url = (
    "https://maps.googleapis.com/maps/api/geocode/json"
    "?latlng=28.6139,77.2090"
    f"&key={API_KEY}"
)

r = requests.get(url)
data = r.json()

if data.get("status") == "OK":
    print("✅ Geocoding API Working")
    print("Address:", data["results"][0]["formatted_address"])
else:
    print("❌ Geocoding Failed")
    print(data)

# --------------------------------------------------
# 2. PLACES API
# --------------------------------------------------
print("\n[2] Testing Places API")

url = (
    "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    "?location=28.6139,77.2090"
    "&radius=5000"
    "&type=hospital"
    f"&key={API_KEY}"
)

r = requests.get(url)
data = r.json()

if data.get("status") == "OK":
    print("✅ Places API Working")

    places = data.get("results", [])[:5]

    print("\nTop Hospitals:")

    for p in places:
        print(
            f"- {p.get('name')} "
            f"(⭐ {p.get('rating', 'N/A')})"
        )

else:
    print("❌ Places API Failed")
    print(data)

# --------------------------------------------------
# 3. PLACE DETAILS API
# --------------------------------------------------
print("\n[3] Testing Place Details API")

if (
    data.get("status") == "OK"
    and len(data["results"]) > 0
):

    place_id = data["results"][0]["place_id"]

    details_url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}"
        "&fields=name,rating,reviews,formatted_phone_number"
        f"&key={API_KEY}"
    )

    details = requests.get(details_url).json()

    if details.get("status") == "OK":
        print("✅ Place Details API Working")

        result = details["result"]

        print("Name:", result.get("name"))
        print("Rating:", result.get("rating"))

        reviews = result.get("reviews", [])

        print("Reviews Found:", len(reviews))

    else:
        print("❌ Place Details API Failed")
        print(details)

# --------------------------------------------------
# 4. DIRECTIONS API
# --------------------------------------------------
print("\n[4] Testing Directions API")

url = (
    "https://maps.googleapis.com/maps/api/directions/json"
    "?origin=Delhi"
    "&destination=Noida"
    f"&key={API_KEY}"
)

r = requests.get(url)
data = r.json()

if data.get("status") == "OK":
    print("✅ Directions API Working")

    leg = data["routes"][0]["legs"][0]

    print("Distance:", leg["distance"]["text"])
    print("Duration:", leg["duration"]["text"])

else:
    print("❌ Directions API Failed")
    print(data)

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------
print("\n")
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
