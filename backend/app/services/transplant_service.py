"""
MEDIX Prototype Backend — Organ Donation & Transplant Service
"""

import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.transplant import TransplantCentre, OrganDonorPledge
from app.schemas.transplant import (
    TransplantCentreResponse,
    TransplantCentresListResponse,
    OrganPledgeRequest,
    OrganPledgeResponse,
    TransplantEducationResponse,
)
from app.config import TRANSPLANT_DISCLAIMER


class TransplantService:
    @staticmethod
    def serialize_centre(tc: TransplantCentre) -> TransplantCentreResponse:
        organs = [o.strip() for o in tc.organs_handled.split(",") if o.strip()]
        return TransplantCentreResponse(
            id=tc.id,
            name=tc.name,
            city=tc.city,
            zone=tc.zone,
            distance=tc.distance,
            organs_handled=organs,
            accreditation=tc.accreditation,
            active_programs=tc.active_programs,
            avg_wait_time=tc.avg_wait_time,
            coordinator_contact=tc.coordinator_contact,
            verified_pledge_count=tc.verified_pledge_count,
            educational_guide=tc.educational_guide,
            is_demonstration=tc.is_demonstration
        )

    @staticmethod
    def list_centres(db: Session, organ: Optional[str] = None) -> TransplantCentresListResponse:
        query = db.query(TransplantCentre)
        filter_organ = None
        if organ and organ.strip() and organ.strip().upper() != "ALL":
            filter_organ = organ.strip()
            query = query.filter(TransplantCentre.organs_handled.ilike(f"%{filter_organ}%"))

        centres = query.all()
        results = [TransplantService.serialize_centre(c) for c in centres]

        return TransplantCentresListResponse(
            total_centres=len(results),
            filter_organ=filter_organ,
            results=results,
            is_simulated=True,
            disclaimer=TRANSPLANT_DISCLAIMER
        )

    @staticmethod
    def get_centre_by_id(db: Session, centre_id: str) -> TransplantCentreResponse:
        clean_id = centre_id.strip()
        tc = db.query(TransplantCentre).filter(TransplantCentre.id == clean_id).first()
        if not tc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transplant centre '{clean_id}' not found in demonstration registry."
            )
        return TransplantService.serialize_centre(tc)

    @staticmethod
    def submit_pledge(db: Session, payload: OrganPledgeRequest) -> OrganPledgeResponse:
        centre_name = None
        if payload.centre_id:
            c = db.query(TransplantCentre).filter(TransplantCentre.id == payload.centre_id).first()
            if c:
                centre_name = c.name
                c.verified_pledge_count += 1

        pledge_id = f"ODP-DEMO-{uuid.uuid4().hex[:6].upper()}"
        pledge_record = OrganDonorPledge(
            id=pledge_id,
            donor_name=payload.donor_name,
            email=payload.email,
            blood_group=payload.blood_group,
            organs_pledged=payload.organs_pledged or "All Vital Organs & Tissues",
            emergency_contact=payload.emergency_contact,
            centre_id=payload.centre_id,
            status="Verified Simulation",
            is_demonstration=True
        )
        db.add(pledge_record)
        db.commit()

        return OrganPledgeResponse(
            success=True,
            pledge_id=pledge_id,
            donor_name=payload.donor_name,
            organs_pledged=pledge_record.organs_pledged,
            centre_name=centre_name,
            status="Verified Simulation",
            is_simulated=True,
            disclaimer=TRANSPLANT_DISCLAIMER
        )

    @staticmethod
    def get_education_guide() -> TransplantEducationResponse:
        return TransplantEducationResponse(
            title="MEDIX Organ Donation & Tissue Transplant Awareness",
            overview=(
                "Organ and tissue donation saves thousands of lives each year. One organ donor can save up to 8 lives "
                "and restore sight or mobility for up to 75 more through tissue donation."
            ),
            living_donor_programs=[
                "Living Kidney Donation: Healthy individuals can donate one kidney safely through laparoscopic surgery.",
                "Living Liver Donation: Segment of liver regenerates to near full volume within weeks for both donor and recipient.",
                "Bone Marrow / PBSC: Simple buccal swab registry with non-invasive apheresis blood draw."
            ],
            deceased_donor_protocols=[
                "Brain Death & Circulatory Death evaluation by independent certified neurological team.",
                "Family consent counseling and honor walk recognition.",
                "National algorithmic matching based on HLA compatibility, blood type, pediatric priority, and medical urgency."
            ],
            official_benchmarks=[
                "NOTTO (National Organ and Tissue Transplant Organization)",
                "UNOS (United Network for Organ Sharing) / OPTN",
                "OrganDonor.gov (US Department of Health & Human Services)"
            ],
            faq=[
                {
                    "q": "Does registering as an organ donor affect emergency medical care?",
                    "a": "No. Emergency physicians and paramedics focus 100% on saving your life. Organ donation is only considered after all life-saving efforts have failed and brain death is certified."
                },
                {
                    "q": "Can older adults or individuals with medical conditions pledge to donate?",
                    "a": "Yes! People of all ages from newborns to senior citizens can be organ donors. Clinical evaluation at the time of donation determines suitability."
                }
            ],
            disclaimer=TRANSPLANT_DISCLAIMER
        )
