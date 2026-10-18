"""
MEDIX Prototype Backend — AI Chest X-ray API Router
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.xray_service import XrayService
from app.schemas.xray import (
    XrayPresetCasesListResponse,
    XrayCaseResponse,
    XrayPredictionResponse,
    XrayStatusResponse,
)

router = APIRouter(prefix="/xray", tags=["AI Chest X-ray"])


@router.get("/status", response_model=XrayStatusResponse, summary="Check X-ray AI Model Inference Availability")
def get_xray_service_status():
    return XrayService.get_status()


@router.get("/cases", response_model=XrayPresetCasesListResponse, summary="List Curated Educational Preset Radiographs")
def get_xray_preset_cases(db: Session = Depends(get_db)):
    return XrayService.list_preset_cases(db)


@router.get("/cases/{case_id}", response_model=XrayCaseResponse, summary="Get Preset Radiograph Case Details")
def get_xray_preset_case_by_id(case_id: str, db: Session = Depends(get_db)):
    return XrayService.get_preset_case_by_id(db, case_id)


@router.post("/predict", response_model=XrayPredictionResponse, summary="Upload Radiograph Image for Triage Assessment")
async def upload_and_predict_xray(
    file: UploadFile = File(..., description="Chest radiograph image (PNG, JPEG, WebP) up to 10MB"),
    db: Session = Depends(get_db)
):
    return await XrayService.evaluate_uploaded_xray(file, db)
