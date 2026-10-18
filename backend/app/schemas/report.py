"""
MEDIX Prototype Backend — Pydantic Schemas: Medical Report Summarizer
Preserves clinical entities, numbers, and warnings without fabricating AI output.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.config import REPORT_DISCLAIMER


class ClinicalHighlights(BaseModel):
    diagnoses: List[str] = Field(default_factory=list)
    vital_signs: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    lab_values: List[str] = Field(default_factory=list)
    warnings_and_allergies: List[str] = Field(default_factory=list)
    dates_and_milestones: List[str] = Field(default_factory=list)


class ReportSummarizeRequest(BaseModel):
    report_text: str = Field(..., min_length=10, max_length=50000)
    patient_context: Optional[str] = Field("General Clinical Report", max_length=120)

    @field_validator("report_text")
    @classmethod
    def validate_report_text(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 10:
            raise ValueError("Report text is too brief for clinical summary (minimum 10 characters required).")
        return clean


class ReportSummarizeResponse(BaseModel):
    success: bool = True
    char_count: int
    source_type: str = "pasted_text"
    extracted_source_excerpt: str
    clinical_highlights: ClinicalHighlights
    summary_text: str
    engine: str = "Local Rule-Based Clinical Terminology Extractor"
    is_external_ai: bool = False
    disclaimer: str = Field(REPORT_DISCLAIMER, example=REPORT_DISCLAIMER)


class ReportStatusResponse(BaseModel):
    gemini_configured: bool = False
    openai_configured: bool = False
    supported_file_types: List[str] = ["text/plain", "application/pdf"]
    max_file_size_mb: int = 5
    fallback_engine: str = "Local Rule-Based Clinical Terminology Extractor"
    message: str
    disclaimer: str = Field(REPORT_DISCLAIMER, example=REPORT_DISCLAIMER)
