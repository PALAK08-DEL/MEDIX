"""
MEDIX Prototype Backend — Patient Profiles & Smart QR Token Service
"""

from datetime import datetime
import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patient import PatientProfile, QRToken
from app.schemas.patient import (
    PatientProfileCreateRequest,
    PatientProfileResponse,
    QRScanSummaryResponse,
    QRTokenRevokeRequest,
    QRTokenRevokeResponse,
)
from app.config import QR_DISCLAIMER, HOST, PORT


class PatientService:
    @staticmethod
    def serialize_profile(p: PatientProfile) -> PatientProfileResponse:
        try:
            allergies = json.loads(p.allergies) if isinstance(p.allergies, str) else p.allergies
        except Exception:
            allergies = []

        try:
            chronic = json.loads(p.chronic_conditions) if isinstance(p.chronic_conditions, str) else p.chronic_conditions
        except Exception:
            chronic = []

        try:
            meds = json.loads(p.medications) if isinstance(p.medications, str) else p.medications
        except Exception:
            meds = []

        resolve_url = f"http://{HOST}:{PORT}/api/v1/patients/qr/{p.security_token}"

        return PatientProfileResponse(
            id=p.id,
            name=p.name,
            age=p.age,
            gender=p.gender,
            blood_group=p.blood_group,
            allergies=allergies or [],
            chronic_conditions=chronic or [],
            medications=meds or [],
            emergency_contact_name=p.emergency_contact_name,
            emergency_contact_phone=p.emergency_contact_phone,
            organ_donor=p.organ_donor,
            emergency_notes=p.emergency_notes,
            security_token=p.security_token,
            qr_resolve_url=resolve_url,
            created_at=p.created_at,
            is_demonstration=p.is_demonstration,
            disclaimer=QR_DISCLAIMER
        )

    @staticmethod
    def list_profiles(db: Session, blood_group: Optional[str] = None) -> List[PatientProfileResponse]:
        query = db.query(PatientProfile)
        if blood_group and blood_group.strip() and blood_group.strip().upper() != "ALL":
            query = query.filter(PatientProfile.blood_group == blood_group.strip().upper())
        profiles = query.all()
        return [PatientService.serialize_profile(p) for p in profiles]

    @staticmethod
    def create_profile(db: Session, payload: PatientProfileCreateRequest) -> PatientProfileResponse:
        pat_id = f"MEDIX-QR-{uuid.uuid4().hex[:6].upper()}"
        sec_token = f"0x{uuid.uuid4().hex[:12].upper()}"

        profile = PatientProfile(
            id=pat_id,
            name=payload.name,
            age=payload.age,
            gender=payload.gender,
            blood_group=payload.blood_group,
            allergies=json.dumps(payload.allergies),
            chronic_conditions=json.dumps(payload.chronic_conditions),
            medications=json.dumps(payload.medications),
            emergency_contact_name=payload.emergency_contact_name,
            emergency_contact_phone=payload.emergency_contact_phone,
            organ_donor=payload.organ_donor,
            emergency_notes=payload.emergency_notes,
            security_token=sec_token,
            is_demonstration=True
        )
        db.add(profile)

        token_record = QRToken(
            token=sec_token,
            patient_id=pat_id,
            access_tier="public",
            is_active=True
        )
        db.add(token_record)
        db.commit()
        db.refresh(profile)

        return PatientService.serialize_profile(profile)

    @staticmethod
    def resolve_qr_token(db: Session, token: str, tier: str = "public") -> QRScanSummaryResponse:
        clean_token = token.strip()
        token_obj = db.query(QRToken).filter(QRToken.token == clean_token).first()

        # Check if revoked
        if token_obj and not token_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=f"This QR token '{clean_token}' has been revoked or expired by the patient. Access denied."
            )

        patient = None
        if token_obj:
            patient = db.query(PatientProfile).filter(PatientProfile.id == token_obj.patient_id).first()
        else:
            patient = db.query(PatientProfile).filter(PatientProfile.security_token == clean_token).first()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical record not found for token '{clean_token}'."
            )

        if str(patient.security_token).startswith("REVOKED_"):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=f"This patient profile's QR code was revoked. Access denied."
            )

        try:
            allergies = json.loads(patient.allergies) if isinstance(patient.allergies, str) else patient.allergies
        except Exception:
            allergies = []

        try:
            chronic = json.loads(patient.chronic_conditions) if isinstance(patient.chronic_conditions, str) else patient.chronic_conditions
        except Exception:
            chronic = []

        try:
            meds = json.loads(patient.medications) if isinstance(patient.medications, str) else patient.medications
        except Exception:
            meds = []

        critical_alerts = []
        if patient.blood_group in ["O-", "B-", "AB-", "A-"]:
            critical_alerts.append(f"Rare Blood Group: {patient.blood_group}")
        if allergies:
            critical_alerts.append(f"Documented Allergies: {', '.join(allergies)}")
        if patient.emergency_notes:
            critical_alerts.append(f"Emergency Note: {patient.emergency_notes}")

        clean_tier = tier.strip().lower()
        extended_data = None
        if clean_tier in ["paramedic", "authorized", "clinical"]:
            extended_data = {
                "patient_id": patient.id,
                "chronic_conditions": chronic or [],
                "current_medications": meds or [],
                "emergency_notes": patient.emergency_notes,
                "created_at": patient.created_at.isoformat() if patient.created_at else None,
                "clinical_access_granted": True
            }

        return QRScanSummaryResponse(
            token=clean_token,
            name=patient.name,
            blood_group=patient.blood_group,
            age=patient.age,
            organ_donor_registered=patient.organ_donor,
            emergency_contact={
                "name": patient.emergency_contact_name,
                "phone": patient.emergency_contact_phone
            },
            primary_allergies_warning=allergies or [],
            critical_alerts=critical_alerts,
            access_tier=clean_tier,
            extended_emr=extended_data,
            disclaimer=QR_DISCLAIMER
        )

    @staticmethod
    def revoke_qr_token(db: Session, payload: QRTokenRevokeRequest) -> QRTokenRevokeResponse:
        clean_token = payload.token.strip()
        token_obj = db.query(QRToken).filter(QRToken.token == clean_token).first()
        patient_obj = db.query(PatientProfile).filter(PatientProfile.security_token == clean_token).first()

        if not token_obj and not patient_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"QR token '{clean_token}' not found."
            )

        if token_obj:
            token_obj.is_active = False
            token_obj.revoked_at = datetime.utcnow()
            if not patient_obj:
                patient_obj = db.query(PatientProfile).filter(PatientProfile.id == token_obj.patient_id).first()

        if patient_obj:
            patient_obj.security_token = f"REVOKED_{uuid.uuid4().hex[:6].upper()}"
            active_tokens = db.query(QRToken).filter(QRToken.patient_id == patient_obj.id).all()
            for tk in active_tokens:
                tk.is_active = False
                tk.revoked_at = datetime.utcnow()

        db.commit()

        return QRTokenRevokeResponse(
            success=True,
            token=clean_token,
            status="Token Revoked",
            message="The QR token has been revoked. Scans will no longer resolve this medical record."
        )
