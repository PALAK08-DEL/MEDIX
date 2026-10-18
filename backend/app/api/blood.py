"""
MEDIX Prototype Backend — Blood Availability & Donation API Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.blood_service import BloodService
from app.schemas.blood import (
    BloodBanksListResponse,
    BloodBankDetailResponse,
    ReservationHoldRequest,
    ReservationHoldResponse,
    DonorPledgeRequest,
    DonorPledgeResponse,
)

router = APIRouter(prefix="/blood", tags=["Blood Availability"])


@router.get("/banks", response_model=BloodBanksListResponse, summary="Query Blood Banks with Filters")
def get_blood_banks(
    blood_group: Optional[str] = Query(None, description="Filter by blood group: A+, A-, B+, B-, AB+, AB-, O+, O-"),
    search: Optional[str] = Query(None, description="Search term matching bank name, zone, or city"),
    city: Optional[str] = Query(None, description="City filter"),
    db: Session = Depends(get_db)
):
    return BloodService.list_blood_banks(db, blood_group=blood_group, search=search, city=city)


@router.get("/banks/{bank_id}", response_model=BloodBankDetailResponse, summary="Get Blood Bank Details by ID")
def get_blood_bank_by_id(bank_id: str, db: Session = Depends(get_db)):
    return BloodService.get_bank_by_id(db, bank_id)


@router.post("/reserve-hold", response_model=ReservationHoldResponse, summary="Place a Simulated Emergency Hold on Blood Units")
def reserve_blood_units(payload: ReservationHoldRequest, db: Session = Depends(get_db)):
    return BloodService.reserve_blood_hold(db, payload)


@router.post("/donor-pledge", response_model=DonorPledgeResponse, status_code=status.HTTP_201_CREATED, summary="Submit Voluntary Blood Donor Pledge")
def submit_blood_donor_pledge(payload: DonorPledgeRequest, db: Session = Depends(get_db)):
    return BloodService.submit_donor_pledge(db, payload)
