"""
MEDIX Prototype Backend — Database Models: Patient Profiles & Opaque QR Tokens
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(16), nullable=False, default="Unspecified")
    blood_group = Column(String(4), nullable=False, index=True)

    # JSON-encoded array strings for clinical safety
    allergies = Column(Text, default="[]")
    chronic_conditions = Column(Text, default="[]")
    medications = Column(Text, default="[]")

    emergency_contact_name = Column(String(128), nullable=False)
    emergency_contact_phone = Column(String(32), nullable=False)
    organ_donor = Column(Boolean, default=False)
    emergency_notes = Column(Text, nullable=True)

    # Opaque unpredictable token (never raw medical records)
    security_token = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_demonstration = Column(Boolean, default=True)

    tokens = relationship("QRToken", back_populates="patient", cascade="all, delete-orphan")


class QRToken(Base):
    __tablename__ = "qr_access_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(64), unique=True, index=True, nullable=False)
    patient_id = Column(String(64), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    access_tier = Column(String(16), default="public")  # "public" (triage only) vs "paramedic" (extended)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    patient = relationship("PatientProfile", back_populates="tokens")
