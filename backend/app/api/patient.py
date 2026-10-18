"""
MEDIX Prototype Backend — Patient Medical Profile & Smart QR API Router
Enforces opaque token resolution (no sensitive medical records in the raw QR payload).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.patient_service import PatientService
from app.schemas.patient import (
    PatientProfileCreateRequest,
    PatientProfileResponse,
    QRScanSummaryResponse,
    QRTokenRevokeRequest,
    QRTokenRevokeResponse,
)

router = APIRouter(prefix="/patients", tags=["Patient Medical QR"])


@router.get("/profiles", response_model=List[PatientProfileResponse], summary="List Patient Profiles")
def list_patient_profiles(
    blood_group: Optional[str] = Query(None, description="Filter by blood group"),
    db: Session = Depends(get_db)
):
    return PatientService.list_profiles(db, blood_group=blood_group)


@router.post("/profile", response_model=PatientProfileResponse, status_code=status.HTTP_201_CREATED, summary="Create Patient Profile")
def create_patient_profile(payload: PatientProfileCreateRequest, db: Session = Depends(get_db)):
    return PatientService.create_profile(db, payload)


@router.get("/qr/{token}", response_model=QRScanSummaryResponse, summary="Resolve Opaque QR Token")
def resolve_qr_token(
    token: str,
    tier: str = Query("public", description="Access tier: 'public' (triage safety) or 'paramedic' (authorized EMR)"),
    db: Session = Depends(get_db)
):
    return PatientService.resolve_qr_token(db, token, tier=tier)


@router.post("/qr/revoke", response_model=QRTokenRevokeResponse, summary="Revoke / Deactivate QR Token")
def revoke_qr_token(payload: QRTokenRevokeRequest, db: Session = Depends(get_db)):
    return PatientService.revoke_qr_token(db, payload)
