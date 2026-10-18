"""
MEDIX Prototype Backend — Realistic Demonstration Data Seeding
All records are strictly fictional for student healthcare hackathon demonstration.
"""

import json
from sqlalchemy.orm import Session

from app.models.blood import BloodBank, BloodInventory
from app.models.transplant import TransplantCentre
from app.models.patient import PatientProfile, QRToken
from app.models.xray import XrayDemoCase


def seed_blood_data(db: Session):
    if db.query(BloodBank).count() > 0:
        return

    banks = [
        {
            "id": "bb-01",
            "name": "Metro Central Blood & Platelet Center",
            "city": "Metro City",
            "zone": "Central Medical District",
            "distance": "2.4 km",
            "phone": "+1 (555) 019-4821",
            "verified_at": "12 mins ago",
            "accepting_donors": True,
            "donation_slots": "Today 2:30 PM, Today 4:00 PM, Tomorrow 10:00 AM",
            "inventory": {
                "A+": 28, "A-": 6, "B+": 34, "B-": 4,
                "AB+": 12, "AB-": 2, "O+": 42, "O-": 3
            }
        },
        {
            "id": "bb-02",
            "name": "St. Jude Regional Blood Bank",
            "city": "Metro City",
            "zone": "East Suburbs",
            "distance": "5.8 km",
            "phone": "+1 (555) 018-7299",
            "verified_at": "45 mins ago",
            "accepting_donors": True,
            "donation_slots": "Today 3:00 PM, Tomorrow 9:00 AM, Tomorrow 1:30 PM",
            "inventory": {
                "A+": 15, "A-": 3, "B+": 20, "B-": 1,
                "AB+": 8, "AB-": 0, "O+": 25, "O-": 1
            }
        },
        {
            "id": "bb-03",
            "name": "Apex Trauma Center Blood Reserve",
            "city": "Northside",
            "zone": "North Medical Quarter",
            "distance": "8.1 km",
            "phone": "+1 (555) 017-3310",
            "verified_at": "5 mins ago",
            "accepting_donors": False,
            "donation_slots": "Emergency Triage Only",
            "inventory": {
                "A+": 40, "A-": 12, "B+": 38, "B-": 8,
                "AB+": 16, "AB-": 4, "O+": 65, "O-": 8
            }
        },
        {
            "id": "bb-04",
            "name": "Community Red Cross Donor Hub",
            "city": "South Valley",
            "zone": "South Campus",
            "distance": "11.3 km",
            "phone": "+1 (555) 014-9923",
            "verified_at": "2 hours ago",
            "accepting_donors": True,
            "donation_slots": "Tomorrow 11:00 AM, Tomorrow 2:00 PM",
            "inventory": {
                "A+": 22, "A-": 5, "B+": 19, "B-": 3,
                "AB+": 10, "AB-": 1, "O+": 31, "O-": 4
            }
        }
    ]

    for b_data in banks:
        inv_dict = b_data.pop("inventory")
        bank = BloodBank(**b_data, is_demonstration=True)
        db.add(bank)
        db.flush()

        for group, units in inv_dict.items():
            if units == 0:
                st = "critical"
            elif units < 5:
                st = "critical"
            elif units < 15:
                st = "moderate"
            else:
                st = "adequate"
            inv = BloodInventory(
                bank_id=bank.id,
                blood_group=group,
                units=units,
                status=st
            )
            db.add(inv)

    db.commit()


def seed_transplant_data(db: Session):
    if db.query(TransplantCentre).count() > 0:
        return

    centres = [
        {
            "id": "tc-01",
            "name": "Metro Institute of Transplantation & Organ Care",
            "city": "Metro City",
            "zone": "University Medical District",
            "distance": "3.1 km",
            "organs_handled": "Kidney, Liver, Pancreas, Cornea",
            "accreditation": "National Organ & Tissue Transplant Board (Grade A)",
            "active_programs": 6,
            "avg_wait_time": "4-6 months (Subject to acuity)",
            "coordinator_contact": "+1 (555) 019-3388",
            "verified_pledge_count": 142,
            "educational_guide": "Specialized in paired kidney exchange and living donor laparoscopic nephrectomy."
        },
        {
            "id": "tc-02",
            "name": "St. Jude Comprehensive Heart & Lung Center",
            "city": "Metro City",
            "zone": "East Suburbs",
            "distance": "6.4 km",
            "organs_handled": "Heart, Lung, Heart-Lung Combined",
            "accreditation": "Cardiopulmonary Transplant Alliance Certified",
            "active_programs": 4,
            "avg_wait_time": "3-8 months (Acuity dependent)",
            "coordinator_contact": "+1 (555) 018-4420",
            "verified_pledge_count": 89,
            "educational_guide": "State-of-the-art ECMO retrieval unit and thoracic allocation expertise."
        },
        {
            "id": "tc-03",
            "name": "Apex Regional Tissue & Eye Bank",
            "city": "Northside",
            "zone": "North Medical Quarter",
            "distance": "8.5 km",
            "organs_handled": "Cornea, Skin, Bone Graft, Heart Valves",
            "accreditation": "International Tissue Banking Federation",
            "active_programs": 5,
            "avg_wait_time": "2-4 weeks",
            "coordinator_contact": "+1 (555) 017-6611",
            "verified_pledge_count": 312,
            "educational_guide": "Provides 24/7 post-mortem tissue harvesting and sight-restoration cornea banking."
        },
        {
            "id": "tc-04",
            "name": "Children's Pediatric Transplant Foundation",
            "city": "South Valley",
            "zone": "South Campus",
            "distance": "12.0 km",
            "organs_handled": "Pediatric Kidney, Liver Segment, Bone Marrow",
            "accreditation": "Pediatric Transplant Network of North America",
            "active_programs": 3,
            "avg_wait_time": "Priority status for minors",
            "coordinator_contact": "+1 (555) 014-7700",
            "verified_pledge_count": 76,
            "educational_guide": "Dedicated family counseling and specialized pediatric size-matched living donor grafts."
        }
    ]

    for c_data in centres:
        centre = TransplantCentre(**c_data, is_demonstration=True)
        db.add(centre)

    db.commit()


def seed_patient_data(db: Session):
    if db.query(PatientProfile).count() > 0:
        return

    patients = [
        {
            "id": "MEDIX-QR-8821",
            "name": "Alex Chen",
            "age": 29,
            "gender": "Non-Binary",
            "blood_group": "O-",
            "allergies": json.dumps(["Penicillin", "Peanuts"]),
            "chronic_conditions": json.dumps(["Mild Asthma"]),
            "medications": json.dumps(["Albuterol Inhaler 90mcg PRN"]),
            "emergency_contact_name": "Sarah Chen (Sister)",
            "emergency_contact_phone": "+1 (555) 019-2834",
            "organ_donor": True,
            "emergency_notes": "Carries EpiPen in backpack. Universal RBC donor.",
            "security_token": "0x9F4C82A1B7D3"
        },
        {
            "id": "MEDIX-QR-5402",
            "name": "Elena Rostova",
            "age": 42,
            "gender": "Female",
            "blood_group": "B+",
            "allergies": json.dumps(["Sulfa Drugs", "Codeine"]),
            "chronic_conditions": json.dumps(["Type 2 Diabetes", "Hypertension"]),
            "medications": json.dumps(["Metformin 500mg BID", "Lisinopril 10mg daily"]),
            "emergency_contact_name": "Mikhail Rostov (Spouse)",
            "emergency_contact_phone": "+1 (555) 018-9921",
            "organ_donor": True,
            "emergency_notes": "Monitors blood glucose daily. Prefers left arm for venipuncture.",
            "security_token": "0x3D7E91C4FA80"
        },
        {
            "id": "MEDIX-QR-1193",
            "name": "Marcus Washington",
            "age": 68,
            "gender": "Male",
            "blood_group": "A+",
            "allergies": json.dumps(["Aspirin (Bronchospasm)", "Latex"]),
            "chronic_conditions": json.dumps(["Coronary Artery Disease", "Hyperlipidemia"]),
            "medications": json.dumps(["Atorvastatin 40mg daily", "Metoprolol 25mg BID"]),
            "emergency_contact_name": "Darius Washington (Son)",
            "emergency_contact_phone": "+1 (555) 017-4401",
            "organ_donor": False,
            "emergency_notes": "Cardiac stent placed 2024. Medically cleared for low-dose heparin.",
            "security_token": "0x8B2A6F1D5E90"
        }
    ]

    for p_data in patients:
        profile = PatientProfile(**p_data, is_demonstration=True)
        db.add(profile)
        tk = QRToken(
            token=p_data["security_token"],
            patient_id=p_data["id"],
            access_tier="public",
            is_active=True
        )
        db.add(tk)

    db.commit()


def seed_xray_data(db: Session):
    if db.query(XrayDemoCase).count() > 0:
        return

    cases = [
        {
            "id": "xray-case-1",
            "title": "Preset Case 01: Normal Healthy Thorax",
            "patient_ref": "Demo-Ref #CX-8801",
            "view_type": "Posteroanterior (PA) Projection",
            "ground_truth": "Unremarkable Chest Radiograph",
            "classification": "Normal (No Focal Opacity)",
            "pneumonia_confidence": 3.4,
            "normal_confidence": 96.6,
            "risk_tier": "Low Clinical Risk",
            "findings": json.dumps([
                "Clear bilateral lung parenchyma without focal consolidation",
                "Sharp costophrenic and cardiophrenic angles",
                "Normal cardiac silhouette size and mediastinal contours"
            ]),
            "svg_path_type": "normal",
            "is_preset_demo": True
        },
        {
            "id": "xray-case-2",
            "title": "Preset Case 02: Right Lobar Bacterial Pneumonia",
            "patient_ref": "Demo-Ref #CX-8802",
            "view_type": "Posteroanterior (PA) Projection",
            "ground_truth": "Right Middle & Lower Lobe Consolidation",
            "classification": "Bacterial Lobar Pneumonia Detected",
            "pneumonia_confidence": 92.1,
            "normal_confidence": 7.9,
            "risk_tier": "High Risk - Immediate Clinical Attention",
            "findings": json.dumps([
                "Dense airspace consolidation in right middle and lower lobes",
                "Prominent air bronchograms visible within opacity",
                "Blunting of right costophrenic angle suggesting reactive pleural fluid"
            ]),
            "svg_path_type": "bacterial",
            "is_preset_demo": True
        },
        {
            "id": "xray-case-3",
            "title": "Preset Case 03: Bilateral Viral Interstitial Infiltrate",
            "patient_ref": "Demo-Ref #CX-8803",
            "view_type": "Anteroposterior (AP) Portable Projection",
            "ground_truth": "Diffuse Bilateral Ground-Glass Opacities",
            "classification": "Viral Interstitial Pneumonia Pattern",
            "pneumonia_confidence": 84.7,
            "normal_confidence": 15.3,
            "risk_tier": "Moderate-to-High Risk",
            "findings": json.dumps([
                "Diffuse reticular and ground-glass haziness throughout both lung fields",
                "Peribronchial cuffing without dense lobar consolidation",
                "Normal heart size; subsegmental atelectasis in left base"
            ]),
            "svg_path_type": "viral",
            "is_preset_demo": True
        }
    ]

    for c_data in cases:
        case = XrayDemoCase(**c_data)
        db.add(case)

    db.commit()


def seed_all(db: Session):
    seed_blood_data(db)
    seed_transplant_data(db)
    seed_patient_data(db)
    seed_xray_data(db)
