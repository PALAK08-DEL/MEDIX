"""
MEDIX Prototype Backend — Pydantic Schemas: Organ Donation & Transplant Centres
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.config import VALID_BLOOD_GROUPS, TRANSPLANT_DISCLAIMER


class TransplantCentreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., example="tc-01")
    name: str = Field(..., example="Metro Institute of Transplantation & Organ Care")
    city: str = Field("Metro City", example="Metro City")
    zone: str = Field(..., example="University Medical District")
    distance: str = Field(..., example="3.1 km")
    organs_handled: List[str] = Field(default_factory=list, example=["Kidney", "Liver", "Cornea"])
    accreditation: str = Field(..., example="National Organ & Tissue Transplant Board (Grade A)")
    active_programs: int = Field(..., example=6)
    avg_wait_time: str = Field(..., example="4-6 months (Subject to acuity)")
    coordinator_contact: str = Field(..., example="+1 (555) 019-3388")
    verified_pledge_count: int = Field(..., example=142)
    educational_guide: Optional[str] = None
    is_demonstration: bool = True


class TransplantCentresListResponse(BaseModel):
    total_centres: int = Field(..., ge=0, example=4)
    filter_organ: Optional[str] = None
    results: List[TransplantCentreResponse] = Field(default_factory=list)
    is_simulated: bool = True
    disclaimer: str = Field(TRANSPLANT_DISCLAIMER, example=TRANSPLANT_DISCLAIMER)


class OrganPledgeRequest(BaseModel):
    donor_name: str = Field(..., min_length=2, max_length=120, example="Morgan Reed")
    email: str = Field(..., min_length=5, max_length=120, example="morgan.reed@example.org")
    blood_group: str = Field(..., min_length=2, max_length=4, example="O+")
    organs_pledged: Optional[str] = Field("All Vital Organs & Tissues", max_length=256)
    emergency_contact: str = Field(..., min_length=3, max_length=120, example="Alex Reed (+1 555-014-9988)")
    centre_id: Optional[str] = Field(None, max_length=32, example="tc-01")

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_GROUPS:
            raise ValueError(f"Invalid blood group '{v}'. Valid options: {', '.join(VALID_BLOOD_GROUPS)}")
        return clean

    @field_validator("donor_name")
    @classmethod
    def validate_donor_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Donor name must be at least 2 characters.")
        return clean


class OrganPledgeResponse(BaseModel):
    success: bool = True
    pledge_id: str = Field(..., example="ODP-DEMO-8849A")
    donor_name: str = Field(..., example="Morgan Reed")
    organs_pledged: str = Field(..., example="All Vital Organs & Tissues")
    centre_name: Optional[str] = Field(None, example="Metro Institute of Transplantation")
    status: str = Field(..., example="Pledge Verified (Simulation Only)")
    is_simulated: bool = True
    disclaimer: str = Field(TRANSPLANT_DISCLAIMER, example=TRANSPLANT_DISCLAIMER)


class TransplantEducationResponse(BaseModel):
    title: str = Field(..., example="MEDIX Organ Donation & Tissue Transplant Awareness")
    overview: str
    living_donor_programs: List[str]
    deceased_donor_protocols: List[str]
    official_benchmarks: List[str]
    faq: List[Dict[str, str]]
    disclaimer: str = Field(TRANSPLANT_DISCLAIMER, example=TRANSPLANT_DISCLAIMER)
