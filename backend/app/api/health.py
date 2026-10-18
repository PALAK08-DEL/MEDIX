"""
MEDIX Prototype Backend — Health Check Endpoint
"""

from datetime import datetime
from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse
from app.config import GENERAL_DISCLAIMER

router = APIRouter(tags=["Health & Status"])


@router.get("/health", response_model=HealthCheckResponse, summary="MEDIX Platform Health Check")
def health_check():
    return HealthCheckResponse(
        status="healthy",
        service="MEDIX Healthcare Platform API",
        database="sqlite_connected",
        prototype_mode=True,
        features_active=[
            "blood_availability",
            "organ_transplant_directory",
            "patient_medical_qr",
            "ai_chest_xray",
            "medical_report_summarizer"
        ],
        timestamp=datetime.utcnow().isoformat() + "Z",
        disclaimer=GENERAL_DISCLAIMER
    )
