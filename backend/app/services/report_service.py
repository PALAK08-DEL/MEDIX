"""
MEDIX Prototype Backend — Medical Report Summarizer & Clinical Extractor Service
Preserves clinical values, medications, vitals, and warnings without fabricating facts.
Supports plain text and PDF document parsing.
"""

import io
import re
from typing import Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.report import ReportSummaryLog
from app.schemas.report import (
    ClinicalHighlights,
    ReportSummarizeRequest,
    ReportSummarizeResponse,
    ReportStatusResponse,
)
from app.config import (
    REPORT_DISCLAIMER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    MAX_REPORT_FILE_SIZE_BYTES,
    SUPPORTED_REPORT_TYPES,
)


class ReportService:
    @staticmethod
    def extract_clinical_highlights(text: str) -> ClinicalHighlights:
        # 1. Vital Signs
        vitals = []
        bp_match = re.findall(r'(?:BP|blood pressure)[:\s]*(\d{2,3}\s*/\s*\d{2,3}(?:\s*mmHg)?)', text, re.IGNORECASE)
        for bp in bp_match:
            vitals.append(f"BP: {bp.strip()} mmHg" if "mmHg" not in bp else f"BP: {bp.strip()}")

        hr_match = re.findall(r'(?:HR|heart rate|pulse)[:\s]*(\d{2,3}(?:\s*bpm)?)', text, re.IGNORECASE)
        for hr in hr_match:
            vitals.append(f"HR: {hr.strip()} bpm" if "bpm" not in hr else f"HR: {hr.strip()}")

        temp_match = re.findall(r'(?:temp|temperature)[:\s]*(\d{2}(?:\.\d)?\s*°?[CF])', text, re.IGNORECASE)
        for t in temp_match:
            vitals.append(f"Temp: {t.strip()}")

        spo2_match = re.findall(r'(?:SpO2|pulse ox|oxygen sat)[:\s]*(\d{2,3}\s*%)', text, re.IGNORECASE)
        for sp in spo2_match:
            vitals.append(f"SpO2: {sp.strip()}")

        # 2. Lab values
        labs = []
        lab_patterns = [
            r'(\b(?:HbA1c|glucose|wbc|rbc|platelets?|creatinine|potassium|sodium|hemoglobin|hematocrit|bun|alt|ast|troponin)[:\s]*[<>]?\s*\d+(?:\.\d+)?(?:\s*[%a-zA-Z/]+)?)',
        ]
        for pat in lab_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                val = match.group(1).strip()
                if len(val) < 40 and val not in labs:
                    labs.append(val)

        # 3. Medications (drug name + dosage)
        meds = []
        med_pattern = r'\b([A-Z][a-z]{2,20}\s+\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|units?)(?:\s+(?:daily|BID|TID|QID|PRN|subQ|oral|IV))?)\b'
        for match in re.finditer(med_pattern, text):
            m = match.group(1).strip()
            if m not in meds:
                meds.append(m)

        # 4. Warnings & Allergies
        warnings = []
        allergy_matches = re.findall(r'((?:allerg(?:y|ies)|adverse reaction|contraindication)[:\s]*[^\n\.\;]+)', text, re.IGNORECASE)
        for a in allergy_matches:
            warnings.append(a.strip())

        if re.search(r'\bNKDA\b|\bno known drug allergies\b', text, re.IGNORECASE):
            warnings.append("NKDA (No Known Drug Allergies)")

        # 5. Diagnoses & Clinical Impressions
        diagnoses = []
        diag_matches = re.findall(r'((?:diagnosis|diagnosed with|impression|assessment|chief complaint)[:\s]*[^\n\.\;]+)', text, re.IGNORECASE)
        for d in diag_matches:
            val = d.strip()
            if len(val) > 4:
                diagnoses.append(val)

        common_conditions = [
            "Type 1 Diabetes", "Type 2 Diabetes", "Hypertension", "Asthma",
            "Pneumonia", "Acute Bronchitis", "COPD", "Coronary Artery Disease",
            "Chronic Kidney Disease", "Atrial Fibrillation", "Heart Failure"
        ]
        for cond in common_conditions:
            if re.search(r'\b' + re.escape(cond) + r'\b', text, re.IGNORECASE):
                if cond not in diagnoses:
                    diagnoses.append(f"Identified Condition: {cond}")

        # 6. Dates & Milestones
        dates = []
        date_matches = re.findall(r'\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b', text)
        for d in date_matches[:5]:
            if d not in dates:
                dates.append(d)

        return ClinicalHighlights(
            diagnoses=diagnoses[:6],
            vital_signs=vitals[:6],
            medications=meds[:6],
            lab_values=labs[:6],
            warnings_and_allergies=warnings[:6],
            dates_and_milestones=dates[:4]
        )

    @staticmethod
    def generate_extractive_summary(text: str, highlights: ClinicalHighlights) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        selected_lines = []

        keywords = ["diagnosis", "impression", "assessment", "plan", "allergy", "prescribe", "rx", "vital", "bp", "temperature"]
        for line in lines:
            if any(k in line.lower() for k in keywords):
                if len(line) > 10 and line not in selected_lines:
                    selected_lines.append(line)

        if not selected_lines:
            selected_lines = lines[:3]

        bullet_points = "\n".join([f"• {sl}" for sl in selected_lines[:5]])

        summary = (
            f"CLINICAL SUMMARY (Rule-Based Extractive Analysis):\n"
            f"{bullet_points}\n\n"
            f"KEY ENTITIES IDENTIFIED:\n"
            f"- Vital Signs: {', '.join(highlights.vital_signs) if highlights.vital_signs else 'None documented'}\n"
            f"- Prescribed Medications: {', '.join(highlights.medications) if highlights.medications else 'None documented'}\n"
            f"- Primary Diagnoses/Impressions: {', '.join(highlights.diagnoses) if highlights.diagnoses else 'Unspecified in source text'}\n"
            f"- Documented Warnings/Allergies: {', '.join(highlights.warnings_and_allergies) if highlights.warnings_and_allergies else 'None explicitly noted'}"
        )
        return summary

    @staticmethod
    def get_service_status() -> ReportStatusResponse:
        has_gemini = bool(GEMINI_API_KEY)
        has_openai = bool(OPENAI_API_KEY)
        msg = (
            "External LLM API key configured. Live generative summarization active."
            if (has_gemini or has_openai)
            else "No external LLM API key configured in .env. Local rule-based clinical entity extraction is active without external data transfer."
        )
        return ReportStatusResponse(
            gemini_configured=has_gemini,
            openai_configured=has_openai,
            supported_file_types=SUPPORTED_REPORT_TYPES,
            max_file_size_mb=MAX_REPORT_FILE_SIZE_BYTES // (1024 * 1024),
            fallback_engine="Local Rule-Based Clinical Terminology Extractor",
            message=msg,
            disclaimer=REPORT_DISCLAIMER
        )

    @staticmethod
    def summarize_text(payload: ReportSummarizeRequest, db: Session, source_type: str = "pasted_text") -> ReportSummarizeResponse:
        raw_text = payload.report_text.strip()
        highlights = ReportService.extract_clinical_highlights(raw_text)
        summary = ReportService.generate_extractive_summary(raw_text, highlights)

        try:
            log_record = ReportSummaryLog(
                source_type=source_type,
                char_count=len(raw_text),
                summary_length_chars=len(summary),
                engine_used="Local Rule-Based Clinical Terminology Extractor",
                is_demonstration=True
            )
            db.add(log_record)
            db.commit()
        except Exception:
            db.rollback()

        excerpt = raw_text[:350] + ("..." if len(raw_text) > 350 else "")

        return ReportSummarizeResponse(
            success=True,
            char_count=len(raw_text),
            source_type=source_type,
            extracted_source_excerpt=excerpt,
            clinical_highlights=highlights,
            summary_text=summary,
            engine="Local Rule-Based Clinical Terminology Extractor",
            is_external_ai=False,
            disclaimer=REPORT_DISCLAIMER
        )

    @staticmethod
    async def parse_and_summarize_file(file: UploadFile, db: Session) -> ReportSummarizeResponse:
        content_type = file.content_type or ""
        filename = (file.filename or "").lower()

        is_text = content_type == "text/plain" or filename.endswith(".txt")
        is_pdf = content_type == "application/pdf" or filename.endswith(".pdf")

        if not (is_text or is_pdf):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported document type '{content_type}'. Supported file formats: plain text (.txt) and PDF (.pdf)."
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded document is empty (0 bytes)."
            )

        if file_size > MAX_REPORT_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Document exceeds {MAX_REPORT_FILE_SIZE_BYTES // (1024 * 1024)} MB limit."
            )

        extracted_text = ""
        if is_text:
            try:
                extracted_text = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    extracted_text = content.decode("latin-1")
                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unable to decode plain text document. Please verify UTF-8 encoding."
                    )
        elif is_pdf:
            try:
                import pypdf
                pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                pages_text = []
                for p in pdf_reader.pages:
                    txt = p.extract_text()
                    if txt:
                        pages_text.append(txt)
                extracted_text = "\n".join(pages_text).strip()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unable to parse PDF report: {str(e)}"
                )

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded document does not contain readable text (minimum 10 characters required)."
            )

        req = ReportSummarizeRequest(
            report_text=extracted_text,
            patient_context=f"Uploaded File: {file.filename}"
        )
        return ReportService.summarize_text(req, db, source_type="file_upload")
