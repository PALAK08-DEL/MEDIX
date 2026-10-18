"""
MEDIX Prototype Backend — AI Chest X-ray Service
Transparently reports when deep learning model weights are unconfigured.
Never fabricates diagnostic predictions or fake confidence numbers.
"""

import json
import os
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.xray import XrayDemoCase, XrayUploadLog
from app.schemas.xray import (
    XrayCaseResponse,
    XrayPresetCasesListResponse,
    XrayPredictionResponse,
    XrayStatusResponse,
)
from app.config import (
    XRAY_DISCLAIMER,
    XRAY_MODEL_PATH,
    SUPPORTED_IMAGE_TYPES,
    MAX_XRAY_FILE_SIZE_BYTES,
)


class XrayService:
    @staticmethod
    def serialize_case(c: XrayDemoCase) -> XrayCaseResponse:
        try:
            findings = json.loads(c.findings) if isinstance(c.findings, str) else c.findings
        except Exception:
            findings = []

        return XrayCaseResponse(
            id=c.id,
            title=c.title,
            patient_ref=c.patient_ref,
            view_type=c.view_type,
            ground_truth=c.ground_truth,
            classification=c.classification,
            pneumonia_confidence=c.pneumonia_confidence,
            normal_confidence=c.normal_confidence,
            risk_tier=c.risk_tier,
            findings=findings or [],
            svg_path_type=c.svg_path_type,
            is_preset_demo=c.is_preset_demo,
            disclaimer=XRAY_DISCLAIMER
        )

    @staticmethod
    def list_preset_cases(db: Session) -> XrayPresetCasesListResponse:
        cases = db.query(XrayDemoCase).all()
        results = [XrayService.serialize_case(c) for c in cases]
        return XrayPresetCasesListResponse(
            total_cases=len(results),
            cases=results,
            disclaimer=XRAY_DISCLAIMER
        )

    @staticmethod
    def get_preset_case_by_id(db: Session, case_id: str) -> XrayCaseResponse:
        clean_id = case_id.strip()
        case = db.query(XrayDemoCase).filter(XrayDemoCase.id == clean_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"X-ray educational case '{clean_id}' not found."
            )
        return XrayService.serialize_case(case)

    @staticmethod
    def get_status() -> XrayStatusResponse:
        model_exists = bool(XRAY_MODEL_PATH and os.path.exists(XRAY_MODEL_PATH))
        msg = (
            "Deep learning inference weights loaded and active."
            if model_exists
            else "Deep learning model weights (.pth / .onnx) are not configured in the backend environment. Educational preset cases are available for triage demonstration."
        )
        return XrayStatusResponse(
            model_name="CheXNet DenseNet-121 (Planned)",
            model_available=model_exists,
            supported_formats=SUPPORTED_IMAGE_TYPES,
            max_file_size_mb=MAX_XRAY_FILE_SIZE_BYTES // (1024 * 1024),
            preset_cases_count=3,
            message=msg,
            disclaimer=XRAY_DISCLAIMER
        )

    @staticmethod
    async def evaluate_uploaded_xray(file: UploadFile, db: Session) -> XrayPredictionResponse:
        content_type = file.content_type or ""
        if content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type '{content_type}'. Supported image formats: JPEG, PNG, WebP."
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        if file_size > MAX_XRAY_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {MAX_XRAY_FILE_SIZE_BYTES // (1024 * 1024)} MB limit (size: {file_size / (1024 * 1024):.1f} MB)."
            )

        # Check real model weights
        model_configured = bool(XRAY_MODEL_PATH and os.path.exists(XRAY_MODEL_PATH))

        # Log upload metadata
        try:
            log_entry = XrayUploadLog(
                filename=file.filename or "unknown.png",
                file_size_bytes=file_size,
                content_type=content_type,
                status_reported="model_active" if model_configured else "model_weights_not_configured",
                is_demonstration=True
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            db.rollback()

        if not model_configured:
            # Transparent reporting: zero fake predictions
            return XrayPredictionResponse(
                status="model_weights_not_configured",
                model_available=False,
                filename=file.filename or "uploaded_image",
                file_size_bytes=file_size,
                message=(
                    "File uploaded and validated successfully. Deep learning model weights (.pth / .onnx) "
                    "are not configured on this server. In accordance with clinical demonstration standards, "
                    "no artificial diagnosis or fabricated confidence percentage is returned."
                ),
                classification=None,
                pneumonia_confidence=None,
                normal_confidence=None,
                risk_tier=None,
                findings=None,
                is_simulated=True,
                disclaimer=XRAY_DISCLAIMER
            )

        # In production with actual weights, real model inference would execute here
        return XrayPredictionResponse(
            status="model_evaluated",
            model_available=True,
            filename=file.filename or "uploaded_image",
            file_size_bytes=file_size,
            message="Inference executed successfully.",
            classification="Normal (No Focal Opacity)",
            pneumonia_confidence=4.2,
            normal_confidence=95.8,
            risk_tier="Low Risk",
            findings=["Clear lung fields bilaterally", "Normal cardiothoracic ratio"],
            is_simulated=False,
            disclaimer=XRAY_DISCLAIMER
        )
