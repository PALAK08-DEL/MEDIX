"""
MEDIX Prototype Backend — Database Models: Medical Report Summarizer
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class ReportSummaryLog(Base):
    __tablename__ = "report_summary_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(32), default="pasted_text")  # "pasted_text" or "file_upload"
    char_count = Column(Integer, nullable=False, default=0)
    summary_length_chars = Column(Integer, nullable=False, default=0)
    engine_used = Column(String(64), default="local_rule_based_extractor")
    processed_at = Column(DateTime, default=datetime.utcnow)
    is_demonstration = Column(Boolean, default=True)
