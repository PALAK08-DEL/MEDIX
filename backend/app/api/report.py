"""
MEDIX Prototype Backend — Medical Report Summarizer API Router
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.report_service import ReportService
from app.schemas.report import (
    ReportSummarizeRequest,
    ReportSummarizeResponse,
    ReportStatusResponse,
)

router = APIRouter(prefix="/reports", tags=["Medical Report Summarizer"])


@router.get("/status", response_model=ReportStatusResponse, summary="Check Report Summarizer Provider Status")
def get_report_service_status():
    return ReportService.get_service_status()


@router.post("/summarize", response_model=ReportSummarizeResponse, summary="Summarize Pasted Clinical Report Text")
def summarize_clinical_report(
    payload: ReportSummarizeRequest,
    db: Session = Depends(get_db)
):
    return ReportService.summarize_text(payload, db, source_type="pasted_text")


@router.post("/upload", response_model=ReportSummarizeResponse, summary="Upload Document (.txt or .pdf) for Summarization")
async def upload_and_summarize_report(
    file: UploadFile = File(..., description="Medical report file (.txt or .pdf) up to 5MB"),
    db: Session = Depends(get_db)
):
    return await ReportService.parse_and_summarize_file(file, db)
