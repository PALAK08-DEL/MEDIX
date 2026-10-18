"""
MEDIX Prototype Backend — Blood Availability & Reservation Service
"""

from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.blood import BloodBank, BloodInventory, BloodReservation, BloodDonorPledge
from app.schemas.blood import (
    BloodBankDetailResponse,
    BloodInventoryItemResponse,
    BloodBanksListResponse,
    ReservationHoldRequest,
    ReservationHoldResponse,
    DonorPledgeRequest,
    DonorPledgeResponse,
)
from app.config import VALID_BLOOD_GROUPS, BLOOD_DISCLAIMER


class BloodService:
    @staticmethod
    def serialize_bank(bank: BloodBank) -> BloodBankDetailResponse:
        slots = [s.strip() for s in bank.donation_slots.split(",") if s.strip()] if bank.donation_slots else []
        inventory_items = [
            BloodInventoryItemResponse(
                blood_group=inv.blood_group,
                units=inv.units,
                status=inv.status,
                updated_at=inv.updated_at
            )
            for inv in sorted(bank.inventory, key=lambda x: x.blood_group)
        ]
        return BloodBankDetailResponse(
            id=bank.id,
            name=bank.name,
            city=bank.city,
            zone=bank.zone,
            distance=bank.distance,
            phone=bank.phone,
            verified_at=bank.verified_at,
            accepting_donors=bank.accepting_donors,
            donation_slots=slots,
            inventory=inventory_items,
            is_demonstration=bank.is_demonstration
        )

    @staticmethod
    def list_blood_banks(
        db: Session,
        blood_group: Optional[str] = None,
        search: Optional[str] = None,
        city: Optional[str] = None
    ) -> BloodBanksListResponse:
        query = db.query(BloodBank)

        if city and city.strip() and city.strip().upper() != "ALL":
            query = query.filter(BloodBank.city.ilike(f"%{city.strip()}%"))

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                (BloodBank.name.ilike(term)) |
                (BloodBank.zone.ilike(term)) |
                (BloodBank.city.ilike(term))
            )

        banks = query.all()
        results: List[BloodBankDetailResponse] = []

        clean_group = blood_group.strip().upper() if blood_group else None
        if clean_group and clean_group != "ALL" and clean_group not in VALID_BLOOD_GROUPS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid blood group '{clean_group}'. Valid options: {', '.join(VALID_BLOOD_GROUPS)}"
            )

        for b in banks:
            serialized = BloodService.serialize_bank(b)
            if clean_group and clean_group != "ALL":
                filtered_inv = [item for item in serialized.inventory if item.blood_group == clean_group]
                serialized.inventory = filtered_inv
            results.append(serialized)

        return BloodBanksListResponse(
            total_banks=len(results),
            filters_applied={"blood_group": clean_group, "search": search, "city": city},
            results=results,
            is_simulated=True,
            disclaimer=BLOOD_DISCLAIMER
        )

    @staticmethod
    def get_bank_by_id(db: Session, bank_id: str) -> BloodBankDetailResponse:
        bank = db.query(BloodBank).filter(BloodBank.id == bank_id.strip()).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blood bank '{bank_id}' not found in demonstration registry."
            )
        return BloodService.serialize_bank(bank)

    @staticmethod
    def reserve_blood_hold(db: Session, payload: ReservationHoldRequest) -> ReservationHoldResponse:
        # Check bank
        bank = db.query(BloodBank).filter(BloodBank.id == payload.bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blood bank '{payload.bank_id}' does not exist."
            )

        # Atomic reservation check
        inv = db.query(BloodInventory).filter(
            BloodInventory.bank_id == payload.bank_id,
            BloodInventory.blood_group == payload.blood_group
        ).first()

        if not inv or inv.units < payload.units:
            avail = inv.units if inv else 0
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient simulated stock for {payload.blood_group} at {bank.name}. Available: {avail} unit(s), Requested: {payload.units} unit(s)."
            )

        # Decrement units safely
        inv.units -= payload.units
        if inv.units == 0:
            inv.status = "critical"
        elif inv.units < 5:
            inv.status = "critical"
        elif inv.units < 15:
            inv.status = "moderate"
        else:
            inv.status = "adequate"

        res_id = f"HOLD-DEMO-{uuid.uuid4().hex[:6].upper()}"
        expires = datetime.utcnow() + timedelta(minutes=45)

        reservation = BloodReservation(
            id=res_id,
            bank_id=bank.id,
            blood_group=payload.blood_group,
            units_reserved=payload.units,
            status="Hold Confirmed (45 Min Window)",
            reserved_at=datetime.utcnow(),
            expires_at=expires,
            is_demonstration=True
        )

        db.add(reservation)
        db.commit()
        db.refresh(inv)

        return ReservationHoldResponse(
            success=True,
            reservation_id=res_id,
            bank_id=bank.id,
            bank_name=bank.name,
            blood_group=payload.blood_group,
            units_reserved=payload.units,
            status="Hold Confirmed (45 Min Expiry Window)",
            expires_at=expires,
            remaining_bank_units=inv.units,
            is_simulated=True,
            disclaimer=BLOOD_DISCLAIMER
        )

    @staticmethod
    def submit_donor_pledge(db: Session, payload: DonorPledgeRequest) -> DonorPledgeResponse:
        bank_name = None
        if payload.bank_id:
            bank = db.query(BloodBank).filter(BloodBank.id == payload.bank_id).first()
            if bank:
                bank_name = bank.name

        pledge_id = f"PLG-{uuid.uuid4().hex[:6].upper()}"
        pledge = BloodDonorPledge(
            id=pledge_id,
            donor_name=payload.donor_name,
            blood_group=payload.blood_group,
            preferred_slot=payload.preferred_slot,
            bank_id=payload.bank_id,
            created_at=datetime.utcnow(),
            status="Pledge Recorded (Simulation)",
            is_demonstration=True
        )
        db.add(pledge)
        db.commit()

        return DonorPledgeResponse(
            success=True,
            pledge_id=pledge_id,
            donor_name=payload.donor_name,
            blood_group=payload.blood_group,
            preferred_slot=payload.preferred_slot,
            bank_name=bank_name,
            status="Pledge Recorded (Simulation)",
            is_simulated=True,
            disclaimer=BLOOD_DISCLAIMER
        )
