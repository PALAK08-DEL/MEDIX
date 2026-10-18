"""
MEDIX Prototype Backend — Pydantic Schemas: Blood Availability & Donation
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.config import VALID_BLOOD_GROUPS, BLOOD_DISCLAIMER


class BloodInventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    blood_group: str = Field(..., example="O-")
    units: int = Field(..., ge=0, example=3)
    status: str = Field(..., example="critical")
    updated_at: Optional[datetime] = None


class BloodBankDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., example="bb-01")
    name: str = Field(..., example="Metro Central Blood & Platelet Center")
    city: str = Field(..., example="Metro City")
    zone: str = Field(..., example="Central Medical District")
    distance: str = Field(..., example="2.4 km")
    phone: str = Field(..., example="+1 (555) 019-4821")
    verified_at: str = Field(..., example="12 mins ago")
    accepting_donors: bool = Field(True, example=True)
    donation_slots: List[str] = Field(default_factory=list)
    inventory: List[BloodInventoryItemResponse] = Field(default_factory=list)
    is_demonstration: bool = Field(True, example=True)


class BloodBanksListResponse(BaseModel):
    total_banks: int = Field(..., ge=0, example=4)
    filters_applied: Dict[str, Optional[str]] = Field(default_factory=dict)
    results: List[BloodBankDetailResponse] = Field(default_factory=list)
    is_simulated: bool = Field(True, example=True)
    disclaimer: str = Field(BLOOD_DISCLAIMER, example=BLOOD_DISCLAIMER)


class ReservationHoldRequest(BaseModel):
    bank_id: str = Field(..., min_length=1, max_length=32, example="bb-01")
    blood_group: str = Field(..., min_length=2, max_length=4, example="O-")
    units: int = Field(1, ge=1, le=10, example=1)

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_GROUPS:
            raise ValueError(f"Invalid blood group '{v}'. Valid options: {', '.join(VALID_BLOOD_GROUPS)}")
        return clean

    @field_validator("bank_id")
    @classmethod
    def validate_bank_id(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("bank_id cannot be blank.")
        return clean


class ReservationHoldResponse(BaseModel):
    success: bool = True
    reservation_id: str = Field(..., example="HOLD-DEMO-9481A")
    bank_id: str = Field(..., example="bb-01")
    bank_name: str = Field(..., example="Metro Central Blood & Platelet Center")
    blood_group: str = Field(..., example="O-")
    units_reserved: int = Field(..., example=1)
    status: str = Field(..., example="Hold Confirmed (45 Min Expiry Window)")
    expires_at: Optional[datetime] = None
    remaining_bank_units: int = Field(..., ge=0, example=2)
    is_simulated: bool = True
    disclaimer: str = Field(BLOOD_DISCLAIMER, example=BLOOD_DISCLAIMER)


class DonorPledgeRequest(BaseModel):
    donor_name: str = Field(..., min_length=2, max_length=100, example="Sarah Connor")
    blood_group: str = Field(..., min_length=2, max_length=4, example="A+")
    preferred_slot: str = Field(..., min_length=3, max_length=64, example="Tomorrow 10:00 AM")
    bank_id: Optional[str] = Field(None, max_length=32, example="bb-02")

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_GROUPS:
            raise ValueError(f"Invalid blood group '{v}'. Valid options: {', '.join(VALID_BLOOD_GROUPS)}")
        return clean

    @field_validator("donor_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Donor name must be at least 2 characters.")
        return clean


class DonorPledgeResponse(BaseModel):
    success: bool = True
    pledge_id: str = Field(..., example="PLG-DEMO-38291")
    donor_name: str = Field(..., example="Sarah Connor")
    blood_group: str = Field(..., example="A+")
    preferred_slot: str = Field(..., example="Tomorrow 10:00 AM")
    bank_name: Optional[str] = Field(None, example="St. Jude Regional Blood Bank")
    status: str = Field(..., example="Pledge Recorded (Simulation)")
    is_simulated: bool = True
    disclaimer: str = Field(BLOOD_DISCLAIMER, example=BLOOD_DISCLAIMER)
