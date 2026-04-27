from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Booking, Hotel, BookingStatus, User
from app.dependencies import get_current_user
from datetime import datetime
import uuid

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/")
def create_booking(
    hotel_id: str,
    check_in: str,
    check_out: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == uuid.UUID(hotel_id)).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
    nights = (check_out_dt - check_in_dt).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    pet_fee_total = hotel.pet_fee_per_night * nights
    total_amount = pet_fee_total  # room rate would be added from Amadeus offer in full impl

    booking = Booking(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        hotel_id=hotel.id,
        check_in=check_in_dt,
        check_out=check_out_dt,
        total_amount=total_amount,
        pet_fee_total=pet_fee_total,
        status=BookingStatus.pending
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {
        "booking_id": str(booking.id),
        "status": booking.status,
        "hotel": hotel.name,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "pet_fee_total": pet_fee_total,
        "total_amount": total_amount
    }

@router.get("/me")
def get_my_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.tenant_id == current_user.tenant_id
    ).all()
    return {"bookings": [
        {
            "booking_id": str(b.id),
            "hotel_id": str(b.hotel_id),
            "check_in": str(b.check_in),
            "check_out": str(b.check_out),
            "status": b.status,
            "total_amount": b.total_amount,
            "pet_fee_total": b.pet_fee_total
        } for b in bookings
    ]}

@router.patch("/{booking_id}/cancel")
def cancel_booking(booking_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(
        Booking.id == uuid.UUID(booking_id),
        Booking.user_id == current_user.id,
        Booking.tenant_id == current_user.tenant_id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    booking.status = BookingStatus.cancelled
    db.commit()
    return {"message": "Booking cancelled", "booking_id": booking_id}