import requests
import json
import difflib

# ---------------- CITY SPELLING LIST ----------------
KNOWN_CITIES = [
    "Bengaluru",
    "Mysuru",
    "Hassan",
    "Tumakuru",
    "Chikkamagaluru",
    "Mandya",
    "Shivamogga",
    "Davanagere",
    "Ballari",
    "Raichur",
    "Bidar",
    "Kalaburagi",
    "Koppal",
    "Udupi",
    "Dakshina Kannada"
]

def suggest_city_name(user_city):
    """
    Suggest correct city names if spelling is wrong
    """
    if not user_city:
        return []

    return difflib.get_close_matches(
        user_city.strip().title(),
        KNOWN_CITIES,
        n=3,
        cutoff=0.6
    )

# ---------------- HOSPITAL SEARCH ----------------
def get_nearby_hospitals_by_city(city):
    try:
        city_clean = city.strip().lower()

        # ---- Geocoding ----
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {
            "q": f"{city_clean} Karnataka India",
            "format": "json",
            "limit": 1
        }

        geo_res = requests.get(
            geo_url,
            params=geo_params,
            headers={"User-Agent": "CareConnect-App"},
            timeout=10
        )

        geo_data = geo_res.json()
        if not geo_data:
            return [], city_clean.title()

        lat = float(geo_data[0]["lat"])
        lon = float(geo_data[0]["lon"])
        corrected_city = geo_data[0]["display_name"].split(",")[0]

        # ---- Overpass ----
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["amenity"~"hospital|clinic|doctors|pharmacy"](around:50000,{lat},{lon});
          way["amenity"~"hospital|clinic|doctors"](around:50000,{lat},{lon});
          node["healthcare"~"hospital|clinic|doctor"](around:50000,{lat},{lon});
        );
        out center tags;
        """

        res = requests.post(overpass_url, data=query, timeout=30)
        if res.status_code != 200 or not res.text.strip():
            return [], corrected_city

        data = res.json()

        hospitals = []
        seen = set()

        for e in data.get("elements", []):
            tags = e.get("tags", {})
            name = tags.get("name")
            if not name or name in seen:
                continue

            seen.add(name)

            lat_val = e.get("lat") or e.get("center", {}).get("lat")
            lon_val = e.get("lon") or e.get("center", {}).get("lon")

            if lat_val and lon_val:
                hospitals.append({
                    "name": name,
                    "lat": lat_val,
                    "lon": lon_val
                })

        return hospitals, corrected_city

    except Exception:
        return [], city.strip().title()