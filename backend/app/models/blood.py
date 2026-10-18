"""
MEDIX Prototype Backend — Database Models: Blood Availability & Donation
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class BloodBank(Base):
    __tablename__ = "blood_banks"

    id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    city = Column(String(64), nullable=False, default="Metro City")
    zone = Column(String(64), nullable=False)
    distance = Column(String(32), nullable=False)
    phone = Column(String(32), nullable=False)
    verified_at = Column(String(32), default="Recent")
    accepting_donors = Column(Boolean, default=True)
    donation_slots = Column(String(256), default="Today 2:00 PM, Today 4:00 PM, Tomorrow 10:00 AM")
    is_demonstration = Column(Boolean, default=True)

    inventory = relationship("BloodInventory", back_populates="bank", cascade="all, delete-orphan")
    reservations = relationship("BloodReservation", back_populates="bank")


class BloodInventory(Base):
    __tablename__ = "blood_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(String(32), ForeignKey("blood_banks.id", ondelete="CASCADE"), nullable=False)
    blood_group = Column(String(4), nullable=False, index=True)
    units = Column(Integer, nullable=False, default=0)
    status = Column(String(16), nullable=False, default="adequate")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bank = relationship("BloodBank", back_populates="inventory")


class BloodReservation(Base):
    __tablename__ = "blood_reservations"

    id = Column(String(64), primary_key=True, index=True)
    bank_id = Column(String(32), ForeignKey("blood_banks.id"), nullable=False)
    blood_group = Column(String(4), nullable=False)
    units_reserved = Column(Integer, nullable=False, default=1)
    status = Column(String(32), default="Hold Confirmed (Demo)")
    reserved_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_demonstration = Column(Boolean, default=True)

    bank = relationship("BloodBank", back_populates="reservations")


class BloodDonorPledge(Base):
    __tablename__ = "blood_donor_pledges"

    id = Column(String(64), primary_key=True, index=True)
    donor_name = Column(String(128), nullable=False)
    blood_group = Column(String(4), nullable=False)
    preferred_slot = Column(String(64), nullable=False)
    bank_id = Column(String(32), ForeignKey("blood_banks.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(32), default="Pledge Confirmed (Demo)")
    is_demonstration = Column(Boolean, default=True)
