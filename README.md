# MEDIX — Connecting Care. Saving Lives.

> **Next-Generation Centralized Healthcare Interoperability Prototype**  
> *Developed for Healthcare Innovation & Student Hackathon Demonstration*

MEDIX is a modern, unified healthcare web application and API service connecting emergency blood supplies, regional organ donation registries, secure patient medical QR codes, transparent AI radiograph screening, and privacy-preserving clinical report summarization.

---

## The 5 Core Features

1. **Blood Availability Finder**
   - Live simulated regional blood bank registry with search by facility, zone, and city.
   - Filter across all 8 standard ABO/Rh blood groups (`A+`, `A-`, `B+,` `B-`, `AB+`, `AB-`, `O+`, `O-`).
   - Atomic reservation holds with safe SQLite transactions preventing over-allocation.
   - Voluntary blood donor pledge scheduling.

2. **Organ Donation & Transplant Centre**
   - Accredited regional transplant hospital directory with filtering by specialized organ programmes (Kidney, Liver, Heart, Lung, Cornea, Pediatric).
   - Educational guidelines on living and deceased donor matching protocols, family counseling, and official national benchmarks.
   - Simulated donor interest registration and digital donor card minting.

3. **Patient Medical Information with Smart QR**
   - Patient emergency triage profile registration (blood group, allergies, chronic conditions, active medications, emergency contacts).
   - **Zero PHI in QR Code:** Only cryptographically unpredictable opaque tokens (`0x...`) are encoded in the scannable SVG pattern.
   - Tiered access model:
     - **Public Triage Scan:** Vital safety fields only (Blood Group, Age, Emergency Contact, Donor Flag); EMR masked.
     - **Authorized Paramedic View:** Unlocks allergies, chronic conditions, medications, and notes.
   - Dynamic token revocation returning `HTTP 410 Gone`.

4. **AI Chest X-ray Pneumonia Triage**
   - Radiograph upload dropzone supporting PNG, JPEG, and WebP up to 10MB.
   - Transparent AI readiness reporting: Discloses `model_weights_not_configured` when weights are unconfigured, refusing to fabricate fake predictions or confidence percentages.
   - Curated educational case presets with radiologist annotations (Normal, Bacterial Lobar, Viral Interstitial).

5. **Medical Report Summarizer & Clinical Extractor**
   - Supports pasted clinical text and `.txt` / `.pdf` file uploads up to 5MB.
   - Local rule-based clinical entity extractor: parses Blood Pressure, Heart Rate, Temperature, SpO2, Diagnoses, Medications, Lab Values, Allergies, and Dates.
   - Local privacy guarantee: No clinical text is transmitted to external cloud services unless explicitly configured via API keys.

---

## Architecture & Directory Structure

```
medix-prototype/
├── frontend/
│   ├── index.html            # Clean, modern single-page application with hash routing
│   ├── css/
│   │   └── app.css           # Healthcare design system (Teal, Navy, Soft Slate)
│   └── js/
│       ├── api.js            # Centralized REST API client (http://127.0.0.1:8000)
│       ├── qr.js             # Pure JavaScript offline SVG QR code generator
│       └── app.js            # Single-page controller & view router for all 5 features
├── backend/
│   ├── app/
│   │   ├── api/              # REST API route handlers
│   │   │   ├── blood.py
│   │   │   ├── health.py
│   │   │   ├── patient.py
│   │   │   ├── report.py
│   │   │   ├── transplant.py
│   │   │   └── xray.py
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── blood.py
│   │   │   ├── patient.py
│   │   │   ├── report.py
│   │   │   ├── transplant.py
│   │   │   └── xray.py
│   │   ├── schemas/          # Pydantic request & response validation
│   │   │   ├── blood.py
│   │   │   ├── health.py
│   │   │   ├── patient.py
│   │   │   ├── report.py
│   │   │   ├── transplant.py
│   │   │   └── xray.py
│   │   ├── services/         # Modular business logic services
│   │   │   ├── blood_service.py
│   │   │   ├── patient_service.py
│   │   │   ├── report_service.py
│   │   │   ├── transplant_service.py
│   │   │   └── xray_service.py
│   │   ├── data/             # Idempotent demo dataset seeding
│   │   ├── config.py         # Central configuration and CORS settings
│   │   ├── database.py       # SQLite engine and session factory
│   │   └── main.py           # FastAPI application & lifespan startup
│   ├── tests/
│   │   └── test_prototype_features.py # 29 Automated unit/integration tests
│   ├── requirements.txt
│   ├── .env.example
│   └── run.sh
├── start.sh                  # Master one-click startup script
└── README.md
```

---

## Quick Start

### Option 1: Master Launcher (Recommended)
From the `medix-prototype/` folder, run:
```bash
./start.sh
```
This automatically launches:
- **Frontend Web App:** `http://localhost:3001`
- **Backend API:** `http://127.0.0.1:8000`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`

### Option 2: Individual Terminal Commands

**Terminal 1 — Backend:**
```bash
cd backend
./run.sh
```

**Terminal 2 — Frontend:**
```bash
cd frontend
python3 -m http.server 3001
```

---

## Running the Automated Test Suite

The test suite runs against an isolated, temporary in-memory SQLite database, leaving the primary demo database untouched.

```bash
cd backend
pytest tests/test_prototype_features.py -v
```

All 29 tests verify:
- Health check & API root
- Blood bank search, filtering, holds (success & 409 conflict), and donor pledges
- Transplant centre directory, organ filtering, educational guidelines, and pledges
- Patient profile creation, opaque token generation, public vs. paramedic tiered resolution, and token revocation (`HTTP 410 Gone`)
- X-ray engine status, presets, file validation, and honest zero-fabrication reporting
- Report text and PDF extraction, clinical highlight isolation, and empty file rejection

---

## Disclaimer
MEDIX is a student healthcare hackathon proof-of-concept prototype. All patient records, hospital contacts, inventory metrics, and doctor entries are simulated demonstration data. Not connected to real hospital databases, clinical records, or live municipal emergency services.
