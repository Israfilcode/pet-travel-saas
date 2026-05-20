from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Booking, BookingStatus, User
from app.dependencies import get_current_user
from datetime import datetime
import uuid

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/")
def create_booking(
    booking_type: str,
    item_name: str,
    start_date: str,
    end_date: str,
    total_amount: float = 0.0,
    pet_fee_total: float = 0.0,
    external_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if booking_type not in ["hotel", "flight"]:
        raise HTTPException(status_code=400, detail="booking_type must be 'hotel' or 'flight'")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    booking = Booking(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        booking_type=booking_type,
        item_name=item_name,
        external_id=external_id,
        check_in=start_dt,
        check_out=end_dt,
        total_amount=total_amount,
        pet_fee_total=pet_fee_total,
        status=BookingStatus.pending
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Booking saved successfully", "booking_id": str(booking.id), "booking_type": booking.booking_type, "item_name": booking.item_name, "start_date": start_date, "end_date": end_date, "total_amount": booking.total_amount, "pet_fee_total": booking.pet_fee_total, "status": booking.status}

@router.get("/me")
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id, Booking.tenant_id == current_user.tenant_id).all()
    return {"bookings": [{"booking_id": str(b.id), "booking_type": b.booking_type, "item_name": b.item_name, "external_id": b.external_id, "start_date": str(b.check_in), "end_date": str(b.check_out), "status": b.status, "total_amount": b.total_amount, "pet_fee_total": b.pet_fee_total} for b in bookings]}

@router.patch("/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == uuid.UUID(booking_id), Booking.user_id == current_user.id, Booking.tenant_id == current_user.tenant_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    booking.status = BookingStatus.cancelled
    db.commit()
    return {"message": "Booking cancelled", "booking_id": booking_id}

@router.patch("/{booking_id}/edit")
def edit_booking(
    booking_id: str,
    start_date: str = None,
    end_date: str = None,
    item_name: str = None,
    total_amount: float = None,
    pet_fee_total: float = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == uuid.UUID(booking_id), Booking.user_id == current_user.id, Booking.tenant_id == current_user.tenant_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot edit a cancelled booking")
    if start_date:
        booking.check_in = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        booking.check_out = datetime.strptime(end_date, "%Y-%m-%d")
    if item_name:
        booking.item_name = item_name
    if total_amount is not None:
        booking.total_amount = total_amount
    if pet_fee_total is not None:
        booking.pet_fee_total = pet_fee_total
    if booking.check_out < booking.check_in:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    db.commit()
    db.refresh(booking)
    return {"message": "Booking updated successfully", "booking_id": str(booking.id), "booking_type": booking.booking_type, "item_name": booking.item_name, "start_date": str(booking.check_in), "end_date": str(booking.check_out), "total_amount": booking.total_amount, "pet_fee_total": booking.pet_fee_total, "status": booking.status}
