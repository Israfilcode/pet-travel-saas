from fastapi import APIRouter, HTTPException
import requests
import os

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/search")
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    pet_friendly: bool = False,
    pet_size: str = "small"
):
    url = "https://kayak-api.p.rapidapi.com/search-flights"

    payload = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "filterParams": {
            "fs": "cabin=e"
        },
        "searchMetaData": {
            "pageNumber": 1,
            "priceMode": "per-person"
        },
        "userSearchParams": {
            "passengers": ["ADT"],
            "sortMode": "price_a"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "kayak-api.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    data = response.json()

    pet_note = None

    if pet_friendly:
        if pet_size.lower() == "small":
            pet_note = "Small pets may be allowed in cabin depending on airline policy. Please confirm with airline before booking."
        else:
            pet_note = "Large pets usually need cargo or special airline approval. Please confirm with airline before booking."

    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "pet_friendly": pet_friendly,
        "pet_size": pet_size,
        "pet_note": pet_note,
        "flight_results": data
    }