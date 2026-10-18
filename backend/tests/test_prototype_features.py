"""
MEDIX Prototype Backend — Automated Test Suite
Tests all 5 core features against an isolated in-memory SQLite database.
"""

import io
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.data.seed_data import seed_all

# Isolated In-Memory SQLite Database Engine for Safe Mutation Tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    seed_all(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ==============================================================================
# Health & Root Endpoints
# ==============================================================================
def test_root_welcome(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "MEDIX" in data["service"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "sqlite_connected"
    assert len(data["features_active"]) == 5


# ==============================================================================
# 1. Feature 1: Blood Availability Finder
# ==============================================================================
def test_get_blood_banks_all(client):
    response = client.get("/api/v1/blood/banks")
    assert response.status_code == 200
    data = response.json()
    assert data["total_banks"] >= 4
    assert len(data["results"]) >= 4
    assert data["is_simulated"] is True


def test_blood_banks_filter_group(client):
    response = client.get("/api/v1/blood/banks?blood_group=O-")
    assert response.status_code == 200
    data = response.json()
    for bank in data["results"]:
        for item in bank["inventory"]:
            assert item["blood_group"] == "O-"


def test_blood_banks_filter_invalid_group(client):
    response = client.get("/api/v1/blood/banks?blood_group=INVALID")
    assert response.status_code == 400
    assert "Invalid blood group" in response.json()["detail"]


def test_blood_banks_search(client):
    response = client.get("/api/v1/blood/banks?search=Metro")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 1
    assert "Metro" in data["results"][0]["name"]


def test_reserve_blood_hold_success(client):
    payload = {
        "bank_id": "bb-01",
        "blood_group": "O-",
        "units": 1
    }
    response = client.post("/api/v1/blood/reserve-hold", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["reservation_id"].startswith("HOLD-DEMO-")
    assert data["units_reserved"] == 1
    assert data["is_simulated"] is True


def test_reserve_blood_hold_insufficient_stock(client):
    payload = {
        "bank_id": "bb-01",
        "blood_group": "O-",
        "units": 10  # Exceeds inventory (available: 2), within schema max 10
    }
    response = client.post("/api/v1/blood/reserve-hold", json=payload)
    assert response.status_code == 409
    assert "Insufficient simulated stock" in response.json()["detail"]


def test_donor_pledge_submission(client):
    payload = {
        "donor_name": "Sarah Connor",
        "blood_group": "A+",
        "preferred_slot": "2026-10-25 10:00 AM",
        "bank_id": "bb-02"
    }
    response = client.post("/api/v1/blood/donor-pledge", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["pledge_id"].startswith("PLG-")
    assert data["donor_name"] == "Sarah Connor"


# ==============================================================================
# 2. Feature 2: Organ Donation & Transplant Centres
# ==============================================================================
def test_get_transplant_centres(client):
    response = client.get("/api/v1/transplant/centres")
    assert response.status_code == 200
    data = response.json()
    assert data["total_centres"] >= 4
    assert len(data["results"]) >= 4
    assert data["is_simulated"] is True


def test_get_transplant_centres_filter_organ(client):
    response = client.get("/api/v1/transplant/centres?organ=Heart")
    assert response.status_code == 200
    data = response.json()
    for centre in data["results"]:
        assert any("Heart" in o for o in centre["organs_handled"])


def test_transplant_education(client):
    response = client.get("/api/v1/transplant/education")
    assert response.status_code == 200
    data = response.json()
    assert "living_donor_programs" in data
    assert len(data["living_donor_programs"]) >= 2
    assert len(data["faq"]) >= 1


def test_submit_organ_donor_pledge(client):
    payload = {
        "donor_name": "Michael Corvin",
        "email": "michael.corvin@example.org",
        "blood_group": "O+",
        "organs_pledged": "Kidney, Cornea, Tissue",
        "emergency_contact": "Selene (+1 555-019-9944)",
        "centre_id": "tc-01"
    }
    response = client.post("/api/v1/transplant/pledge", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["pledge_id"].startswith("ODP-DEMO-")
    assert data["donor_name"] == "Michael Corvin"


# ==============================================================================
# 3. Feature 3: Patient Medical QR
# ==============================================================================
def test_list_patient_profiles(client):
    response = client.get("/api/v1/patients/profiles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["security_token"].startswith("0x")


def test_create_patient_profile(client):
    payload = {
        "name": "David Miller",
        "age": 35,
        "gender": "Male",
        "blood_group": "B+",
        "allergies": ["Sulfa"],
        "chronic_conditions": ["Hypertension"],
        "medications": ["Amlodipine 5mg"],
        "emergency_contact_name": "Clara Miller",
        "emergency_contact_phone": "+1 (555) 012-3456",
        "organ_donor": True
    }
    response = client.post("/api/v1/patients/profile", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "David Miller"
    assert data["security_token"].startswith("0x")
    assert data["id"].startswith("MEDIX-QR-")


def test_resolve_qr_token_public(client):
    profiles = client.get("/api/v1/patients/profiles").json()
    token = profiles[0]["security_token"]

    response = client.get(f"/api/v1/patients/qr/{token}?tier=public")
    assert response.status_code == 200
    data = response.json()
    assert data["token"] == token
    assert data["name"] == profiles[0]["name"]
    assert data["access_tier"] == "public"
    assert data["extended_emr"] is None  # Public tier does not reveal extended records


def test_resolve_qr_token_paramedic(client):
    profiles = client.get("/api/v1/patients/profiles").json()
    token = profiles[0]["security_token"]

    response = client.get(f"/api/v1/patients/qr/{token}?tier=paramedic")
    assert response.status_code == 200
    data = response.json()
    assert data["access_tier"] == "paramedic"
    assert data["extended_emr"] is not None
    assert "chronic_conditions" in data["extended_emr"]


def test_revoke_qr_token_and_verify_410(client):
    payload = {
        "name": "Test Revocation Patient",
        "age": 40,
        "gender": "Female",
        "blood_group": "A-",
        "allergies": [],
        "chronic_conditions": [],
        "medications": [],
        "emergency_contact_name": "Contact Person",
        "emergency_contact_phone": "+1 555-019-1122",
        "organ_donor": True
    }
    created = client.post("/api/v1/patients/profile", json=payload).json()
    rev_token = created["security_token"]

    # Revoke
    rev_resp = client.post("/api/v1/patients/qr/revoke", json={"token": rev_token})
    assert rev_resp.status_code == 200
    assert rev_resp.json()["success"] is True

    # Resolving revoked token must return HTTP 410 Gone
    gone_resp = client.get(f"/api/v1/patients/qr/{rev_token}")
    assert gone_resp.status_code == 410
    assert "revoked" in gone_resp.json()["detail"].lower()


# ==============================================================================
# 4. Feature 4: AI Chest X-ray Pneumonia Detection
# ==============================================================================
def test_xray_status(client):
    response = client.get("/api/v1/xray/status")
    assert response.status_code == 200
    data = response.json()
    assert "supported_formats" in data
    assert "max_file_size_mb" in data


def test_xray_preset_cases(client):
    response = client.get("/api/v1/xray/cases")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] >= 3
    assert data["cases"][0]["is_preset_demo"] is True


def test_xray_upload_empty_file_fails(client):
    files = {"file": ("empty.png", b"", "image/png")}
    response = client.post("/api/v1/xray/predict", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_xray_upload_unsupported_media_type(client):
    files = {"file": ("test.txt", b"plain text content", "text/plain")}
    response = client.post("/api/v1/xray/predict", files=files)
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]


def test_xray_upload_valid_image_honest_evaluation(client):
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00'
        b'\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    files = {"file": ("chest_radiograph.png", png_bytes, "image/png")}
    response = client.post("/api/v1/xray/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "model_weights_not_configured"
    assert data["model_available"] is False
    assert data["classification"] is None
    assert data["pneumonia_confidence"] is None
    assert "not configured" in data["message"].lower()


# ==============================================================================
# 5. Feature 5: Medical Report Summarizer
# ==============================================================================
def test_report_service_status(client):
    response = client.get("/api/v1/reports/status")
    assert response.status_code == 200
    data = response.json()
    assert "supported_file_types" in data
    assert "fallback_engine" in data


def test_summarize_report_text(client):
    text = (
        "Patient presents with acute fever (38.5 C), BP: 126/80 mmHg, HR: 82 bpm, SpO2: 96%.\n"
        "Impression: Community-Acquired Pneumonia and Type 2 Diabetes.\n"
        "Prescribed Azithromycin 500mg daily. Lab HbA1c: 7.1%. NKDA."
    )
    payload = {"report_text": text, "patient_context": "ER Triage"}
    response = client.post("/api/v1/reports/summarize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["char_count"] == len(text)
    assert data["extracted_source_excerpt"].startswith("Patient presents")

    # Highlights preservation
    h = data["clinical_highlights"]
    assert any("BP:" in v for v in h["vital_signs"])
    assert any("HR:" in v for v in h["vital_signs"])
    assert any("Pneumonia" in d or "Diabetes" in d for d in h["diagnoses"])
    assert any("Azithromycin" in m for m in h["medications"])
    assert any("NKDA" in w for w in h["warnings_and_allergies"])


def test_summarize_report_text_too_short(client):
    payload = {"report_text": "Short"}
    response = client.post("/api/v1/reports/summarize", json=payload)
    assert response.status_code == 422 or response.status_code == 400


def test_upload_report_plain_text(client):
    doc_content = (
        b"PROGRESS NOTES - ICU\n"
        b"BP: 130/85 mmHg, HR: 78 bpm. Impression: Acute Bronchitis.\n"
        b"Prescribed Amoxicillin 500mg TID. Patient has Penicillin allergy: High."
    )
    files = {"file": ("icu_notes.txt", doc_content, "text/plain")}
    response = client.post("/api/v1/reports/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "file_upload" in data["source_type"]
    assert any("BP:" in v for v in data["clinical_highlights"]["vital_signs"])


def test_upload_report_empty_file_fails(client):
    files = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/api/v1/reports/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_report_pdf_valid(client):
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    files = {"file": ("test_report.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/reports/upload", files=files)
    # A blank PDF has no readable text, so it returns 400
    assert response.status_code == 400
    assert "readable text" in response.json()["detail"].lower()
