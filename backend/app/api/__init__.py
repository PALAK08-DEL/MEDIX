"""
MEDIX Prototype Backend — API Routers Package
"""

from app.api.health import router as health_router
from app.api.blood import router as blood_router
from app.api.transplant import router as transplant_router
from app.api.patient import router as patient_router
from app.api.xray import router as xray_router
from app.api.report import router as report_router

__all__ = [
    "health_router",
    "blood_router",
    "transplant_router",
    "patient_router",
    "xray_router",
    "report_router",
]
