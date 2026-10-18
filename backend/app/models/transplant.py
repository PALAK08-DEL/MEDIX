"""
MEDIX Prototype Backend — Database Models: Organ Donation & Transplant Centres
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from app.database import Base


class TransplantCentre(Base):
    __tablename__ = "transplant_centres"

    id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    city = Column(String(64), nullable=False, default="Metro City")
    zone = Column(String(64), nullable=False)
    distance = Column(String(32), nullable=False)
    organs_handled = Column(String(256), nullable=False)
    accreditation = Column(String(128), default="National Organ & Tissue Transplant Board")
    active_programs = Column(Integer, default=5)
    avg_wait_time = Column(String(64), default="Variable by acuity")
    coordinator_contact = Column(String(64), nullable=False)
    verified_pledge_count = Column(Integer, default=120)
    educational_guide = Column(Text, nullable=True)
    is_demonstration = Column(Boolean, default=True)


class OrganDonorPledge(Base):
    __tablename__ = "organ_donor_pledges"

    id = Column(String(64), primary_key=True, index=True)
    donor_name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    blood_group = Column(String(4), nullable=False)
    organs_pledged = Column(String(256), default="All Vital Organs & Tissues")
    emergency_contact = Column(String(64), nullable=False)
    centre_id = Column(String(32), ForeignKey("transplant_centres.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(32), default="Verified Simulation")
    is_demonstration = Column(Boolean, default=True)
