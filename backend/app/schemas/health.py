"""
MEDIX Prototype Backend — Health Check Schemas
"""

from typing import List
from pydantic import BaseModel, Field
from app.config import GENERAL_DISCLAIMER


class HealthCheckResponse(BaseModel):
    status: str = Field("healthy", example="healthy")
    service: str = Field("MEDIX Healthcare Platform API", example="MEDIX Healthcare Platform API")
    database: str = Field("sqlite_connected", example="sqlite_connected")
    prototype_mode: bool = Field(True, example=True)
    features_active: List[str] = Field(default_factory=lambda: [
        "blood_availability",
        "organ_transplant_directory",
        "patient_medical_qr",
        "ai_chest_xray",
        "medical_report_summarizer"
    ])
    timestamp: str
    disclaimer: str = Field(GENERAL_DISCLAIMER, example=GENERAL_DISCLAIMER)
