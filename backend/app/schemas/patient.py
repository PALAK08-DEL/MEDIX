"""
MEDIX Prototype Backend — Pydantic Schemas: Patient Profile & Smart QR
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.config import VALID_BLOOD_GROUPS, QR_DISCLAIMER


class PatientProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, example="Alex Chen")
    age: int = Field(..., ge=1, le=125, example=29)
    gender: str = Field("Other", example="Non-Binary")
    blood_group: str = Field(..., example="O-")
    allergies: List[str] = Field(default_factory=list, example=["Penicillin", "Peanuts"])
    chronic_conditions: List[str] = Field(default_factory=list, example=["Mild Asthma"])
    medications: List[str] = Field(default_factory=list, example=["Albuterol Inhaler PRN"])
    emergency_contact_name: str = Field(..., min_length=2, max_length=120, example="Sarah Chen")
    emergency_contact_phone: str = Field(..., min_length=5, max_length=32, example="+1 (555) 019-2834")
    organ_donor: bool = Field(True, example=True)
    emergency_notes: Optional[str] = Field(None, max_length=500, example="Carries EpiPen in backpack.")

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_GROUPS:
            raise ValueError(f"Invalid blood group '{v}'. Valid options: {', '.join(VALID_BLOOD_GROUPS)}")
        return clean

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Patient name must be at least 2 characters.")
        return clean


class PatientProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., example="MEDIX-QR-8821")
    name: str = Field(..., example="Alex Chen")
    age: int = Field(..., example=29)
    gender: str = Field(..., example="Non-Binary")
    blood_group: str = Field(..., example="O-")
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    emergency_contact_name: str = Field(..., example="Sarah Chen")
    emergency_contact_phone: str = Field(..., example="+1 (555) 019-2834")
    organ_donor: bool = True
    emergency_notes: Optional[str] = None
    security_token: str = Field(..., example="0x9F4C82A1B7D3")
    qr_resolve_url: str = Field(..., example="http://127.0.0.1:8000/api/v1/patients/qr/0x9F4C82A1B7D3")
    created_at: Optional[datetime] = None
    is_demonstration: bool = True
    disclaimer: str = Field(QR_DISCLAIMER, example=QR_DISCLAIMER)


class QRScanSummaryResponse(BaseModel):
    """
    Public resolution payload when scanning the QR token.
    Contains triage vitals safely without exposing extended medical history.
    """
    token: str = Field(..., example="0x9F4C82A1B7D3")
    name: str = Field(..., example="Alex Chen")
    blood_group: str = Field(..., example="O-")
    age: int = Field(..., example=29)
    organ_donor_registered: bool = True
    emergency_contact: Dict[str, str] = Field(default_factory=dict)
    primary_allergies_warning: List[str] = Field(default_factory=list)
    critical_alerts: List[str] = Field(default_factory=list)
    access_tier: str = Field("public", example="public")
    extended_emr: Optional[Dict[str, Any]] = None
    disclaimer: str = Field(QR_DISCLAIMER, example=QR_DISCLAIMER)


class QRTokenRevokeRequest(BaseModel):
    token: str = Field(..., min_length=4, max_length=64, example="0x9F4C82A1B7D3")


class QRTokenRevokeResponse(BaseModel):
    success: bool = True
    token: str
    status: str = "Token Revoked"
    message: str = "The QR token has been revoked. Scans will no longer resolve this medical record."
