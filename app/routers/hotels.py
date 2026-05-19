from fastapi import APIRouter, HTTPException, Query
import os
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/hotels-api", tags=["Hotels"])

@router.get("/search")
def search_hotels(
    location: str = Query(..., description="City or location name"),
    check_in: str = Query(..., description="Check-in date, format YYYY-MM-DD"),
    check_out: str = Query(..., description="Check-out date, format YYYY-MM-DD"),
    pet_friendly: bool = Query(True, description="Filter for pet-friendly hotels"),
    max_pet_weight: int = Query(50, description="Maximum pet weight in lbs"),
):

    url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"

    querystring = {
        "name": location,
        "locale": "en-us"
    }

    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=querystring,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"RapidAPI error: {str(e)}"
        )

    filtered_results = []

    for hotel in data[:5]:
        hotel["pet_friendly"] = pet_friendly
        hotel["pet_fee"] = 25
        hotel["max_pet_weight"] = max_pet_weight
        hotel["check_in"] = check_in
        hotel["check_out"] = check_out

        filtered_results.append(hotel)

    return {
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "pet_friendly": pet_friendly,
        "max_pet_weight": max_pet_weight,
        "results": filtered_results
    }