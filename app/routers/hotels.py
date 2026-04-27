from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Hotel, User
from app.dependencies import get_current_user
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter(prefix="/hotels", tags=["Hotels"])

def get_amadeus():
    from amadeus import Client
    return Client(
        client_id=os.getenv("AMADEUS_CLIENT_ID"),
        client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
    )

@router.get("/search")
def search_hotels(
    city_code: str,
    check_in: str,
    check_out: str,
    pet_friendly: bool = False,
    max_pet_weight: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        amadeus = get_amadeus()
        response = amadeus.shopping.hotel_offers.get(
            cityCode=city_code,
            checkInDate=check_in,
            checkOutDate=check_out
        )
        hotels = response.data
    except Exception as e:
        raise HTTPException(status_code=503, detail="Unable to fetch hotel data. Please try again later.")

    results = []
    for h in hotels:
        hotel_info = h.get("hotel", {})
        amadeus_id = hotel_info.get("hotelId", "")

        # Check or create hotel in DB
        db_hotel = db.query(Hotel).filter(Hotel.amadeus_id == amadeus_id).first()
        if not db_hotel:
            db_hotel = Hotel(
                amadeus_id=amadeus_id,
                name=hotel_info.get("name", "Unknown"),
                city=city_code,
                latitude=hotel_info.get("latitude"),
                longitude=hotel_info.get("longitude"),
                pet_allowed=False,
                max_pet_weight=None,
                pet_fee_per_night=0.0
            )
            db.add(db_hotel)
            db.commit()
            db.refresh(db_hotel)

        # Apply pet filter
        if pet_friendly and not db_hotel.pet_allowed:
            continue
        if max_pet_weight and db_hotel.max_pet_weight and db_hotel.max_pet_weight < max_pet_weight:
            continue

        offer = h.get("offers", [{}])[0]
        results.append({
            "hotel_id": str(db_hotel.id),
            "amadeus_id": amadeus_id,
            "name": db_hotel.name,
            "city": city_code,
            "pet_allowed": db_hotel.pet_allowed,
            "max_pet_weight": db_hotel.max_pet_weight,
            "pet_fee_per_night": db_hotel.pet_fee_per_night,
            "price_per_night": offer.get("price", {}).get("total", "N/A"),
            "currency": offer.get("price", {}).get("currency", "USD"),
        })

    return {"tenant_id": str(current_user.tenant_id), "results": results}

@router.get("/{hotel_id}")
def get_hotel(hotel_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import uuid
    hotel = db.query(Hotel).filter(Hotel.id == uuid.UUID(hotel_id)).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Mock nearby pet amenities
    nearby = [
        {"name": "Central Dog Park", "distance_miles": 0.8, "type": "Dog Park"},
        {"name": "Riverside Trail", "distance_miles": 1.2, "type": "Trail"},
        {"name": "Paws Beach", "distance_miles": 2.5, "type": "Beach"},
    ]

    return {
        "hotel": {
            "id": str(hotel.id),
            "name": hotel.name,
            "city": hotel.city,
            "pet_allowed": hotel.pet_allowed,
            "max_pet_weight": hotel.max_pet_weight,
            "pet_fee_per_night": hotel.pet_fee_per_night,
        },
        "nearby_pet_amenities": nearby
    }

@router.get("/activities")
def get_activities(city_code: str, current_user: User = Depends(get_current_user)):
    try:
        amadeus = get_amadeus()
        response = amadeus.shopping.activities.get(
            latitude=37.3382,
            longitude=-121.8863
        )
        activities = response.data[:5]
        return {"activities": [{"name": a.get("name"), "description": a.get("shortDescription")} for a in activities]}
    except Exception:
        return {"activities": [
            {"name": "Dog-Friendly Hiking Trail", "description": "Scenic trail welcoming dogs on leash"},
            {"name": "Pet Café Downtown", "description": "Coffee shop with outdoor seating for pets"},
            {"name": "City Dog Park", "description": "Fenced off-leash area with water stations"},
        ]}