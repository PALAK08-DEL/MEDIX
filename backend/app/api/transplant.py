"""
MEDIX Prototype Backend — Organ Donation & Transplant Centres API Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.transplant_service import TransplantService
from app.schemas.transplant import (
    TransplantCentresListResponse,
    TransplantCentreResponse,
    OrganPledgeRequest,
    OrganPledgeResponse,
    TransplantEducationResponse,
)

router = APIRouter(prefix="/transplant", tags=["Organ Donation & Transplant"])


@router.get("/centres", response_model=TransplantCentresListResponse, summary="List Transplant Centres")
def get_transplant_centres(
    organ: Optional[str] = Query(None, description="Filter by organ program (e.g. Kidney, Heart, Cornea)"),
    db: Session = Depends(get_db)
):
    return TransplantService.list_centres(db, organ=organ)


@router.get("/centres/{centre_id}", response_model=TransplantCentreResponse, summary="Get Transplant Centre by ID")
def get_transplant_centre_by_id(centre_id: str, db: Session = Depends(get_db)):
    return TransplantService.get_centre_by_id(db, centre_id)


@router.post("/pledge", response_model=OrganPledgeResponse, status_code=status.HTTP_201_CREATED, summary="Submit Organ Donor Pledge")
def submit_organ_donor_pledge(payload: OrganPledgeRequest, db: Session = Depends(get_db)):
    return TransplantService.submit_pledge(db, payload)


@router.get("/education", response_model=TransplantEducationResponse, summary="Organ Donation Educational Guide")
def get_transplant_education():
    return TransplantService.get_education_guide()
