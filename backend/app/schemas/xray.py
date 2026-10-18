"""
MEDIX Prototype Backend — Pydantic Schemas: AI Chest X-ray Demonstrator
Enforces honest reporting when deep learning model weights are not configured.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.config import XRAY_DISCLAIMER


class XrayCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., example="xray-case-2")
    title: str = Field(..., example="Sample Case 02: Right Lobar Bacterial Pneumonia")
    patient_ref: str = Field(..., example="Demo-Ref #CX-8802")
    view_type: str = Field(..., example="Posteroanterior (PA) Projection")
    ground_truth: str = Field(..., example="Right Middle Lobe Consolidation")
    classification: str = Field(..., example="Focal Bacterial Pneumonia Detected")
    pneumonia_confidence: float = Field(..., example=91.4)
    normal_confidence: float = Field(..., example=8.6)
    risk_tier: str = Field(..., example="High Risk - Clinical Attention Recommended")
    findings: List[str] = Field(default_factory=list)
    svg_path_type: str = Field("bacterial", example="bacterial")
    is_preset_demo: bool = True
    disclaimer: str = Field(XRAY_DISCLAIMER, example=XRAY_DISCLAIMER)


class XrayPresetCasesListResponse(BaseModel):
    total_cases: int = Field(..., example=3)
    cases: List[XrayCaseResponse] = Field(default_factory=list)
    disclaimer: str = Field(XRAY_DISCLAIMER, example=XRAY_DISCLAIMER)


class XrayPredictionResponse(BaseModel):
    """
    Inference Response.
    If weights are missing, transparently communicates model_available: False
    without fabricating fake confidence percentages.
    """
    status: str = Field(..., example="model_weights_not_configured")
    model_available: bool = Field(False, example=False)
    filename: str = Field(..., example="patient_cxr.png")
    file_size_bytes: int = Field(..., example=248010)
    message: str = Field(
        ...,
        example="Deep learning model weights not loaded in server environment. Live clinical inference is unavailable."
    )
    classification: Optional[str] = None
    pneumonia_confidence: Optional[float] = None
    normal_confidence: Optional[float] = None
    risk_tier: Optional[str] = None
    findings: Optional[List[str]] = None
    is_simulated: bool = True
    disclaimer: str = Field(XRAY_DISCLAIMER, example=XRAY_DISCLAIMER)


class XrayStatusResponse(BaseModel):
    model_name: str = "CheXNet DenseNet-121 (Planned)"
    model_available: bool = False
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/webp"]
    max_file_size_mb: int = 10
    preset_cases_count: int = 3
    message: str
    disclaimer: str = Field(XRAY_DISCLAIMER, example=XRAY_DISCLAIMER)
