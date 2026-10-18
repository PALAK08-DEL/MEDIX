"""
MEDIX Prototype Backend — Database Models: AI Chest X-ray Demonstrator
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from app.database import Base


class XrayDemoCase(Base):
    __tablename__ = "xray_demo_cases"

    id = Column(String(32), primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    patient_ref = Column(String(64), nullable=False)
    view_type = Column(String(64), default="Posteroanterior (PA) Projection")
    ground_truth = Column(String(128), nullable=False)
    classification = Column(String(128), nullable=False)
    pneumonia_confidence = Column(Float, nullable=False)
    normal_confidence = Column(Float, nullable=False)
    risk_tier = Column(String(64), nullable=False)
    findings = Column(Text, default="[]")  # JSON array string
    svg_path_type = Column(String(32), default="normal")
    is_preset_demo = Column(Boolean, default=True)


class XrayUploadLog(Base):
    __tablename__ = "xray_upload_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_type = Column(String(64), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status_reported = Column(String(64), default="model_weights_not_configured")
    is_demonstration = Column(Boolean, default=True)
