from fastapi import APIRouter, Depends
from app.models.models import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/search")
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    pet_friendly: bool = False,
    pet_size: str = "small",
    current_user: User = Depends(get_current_user)
):
    flights = [
        {"flight_id": "FL-001", "airline": "United Airlines", "flight_number": "UA 487", "origin": origin.upper(), "destination": destination.upper(), "departure": f"{departure_date}T08:30:00", "arrival": f"{departure_date}T11:45:00", "duration": "3h 15m", "price": 289.00, "currency": "USD", "pet_friendly": True, "pet_policy": "Pets allowed in cabin (under 20 lbs) or cargo hold", "pet_fee": 125.00, "seats_available": 4},
        {"flight_id": "FL-002", "airline": "Delta Air Lines", "flight_number": "DL 892", "origin": origin.upper(), "destination": destination.upper(), "departure": f"{departure_date}T12:00:00", "arrival": f"{departure_date}T15:30:00", "duration": "3h 30m", "price": 319.00, "currency": "USD", "pet_friendly": True, "pet_policy": "Small pets allowed in cabin, larger pets in cargo", "pet_fee": 95.00, "seats_available": 2},
        {"flight_id": "FL-003", "airline": "Southwest Airlines", "flight_number": "WN 234", "origin": origin.upper(), "destination": destination.upper(), "departure": f"{departure_date}T16:45:00", "arrival": f"{departure_date}T20:10:00", "duration": "3h 25m", "price": 249.00, "currency": "USD", "pet_friendly": False, "pet_policy": "No pets allowed on this route", "pet_fee": 0.00, "seats_available": 8},
        {"flight_id": "FL-004", "airline": "Alaska Airlines", "flight_number": "AS 771", "origin": origin.upper(), "destination": destination.upper(), "departure": f"{departure_date}T19:20:00", "arrival": f"{departure_date}T22:40:00", "duration": "3h 20m", "price": 275.00, "currency": "USD", "pet_friendly": True, "pet_policy": "Pets welcome in cabin or as checked baggage", "pet_fee": 100.00, "seats_available": 6}
    ]
    if pet_friendly:
        flights = [f for f in flights if f["pet_friendly"]]
    return {"origin": origin.upper(), "destination": destination.upper(), "departure_date": departure_date, "pet_friendly_filter": pet_friendly, "results": flights}
