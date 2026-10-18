"""
MEDIX Prototype Backend — FastAPI Application Entrypoint
Connecting Care. Saving Lives.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import (
    API_V1_PREFIX,
    CORS_ORIGINS,
    GENERAL_DISCLAIMER
)
from app.database import engine, Base, SessionLocal
from app.data.seed_data import seed_all
from app.api.health import router as health_router
from app.api.blood import router as blood_router
from app.api.transplant import router as transplant_router
from app.api.patient import router as patient_router
from app.api.xray import router as xray_router
from app.api.report import router as report_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    Base.metadata.create_all(bind=engine)

    # Seed demonstration datasets idempotently
    db = SessionLocal()
    try:
        seed_all(db)
        print("[MEDIX Prototype Backend] Database schema verified & demo records seeded.")
    except Exception as e:
        print(f"[MEDIX Prototype Backend] Seed notice: {e}")
    finally:
        db.close()

    yield


app = FastAPI(
    title="MEDIX Healthcare Prototype API",
    description=(
        "Centralized healthcare interoperability and diagnostic demonstration platform.\n\n"
        "**Core Demonstration Modules:**\n"
        "1. Blood Availability & Reservation Holds\n"
        "2. Organ Donation & Regional Transplant Directory\n"
        "3. Patient Medical Information with Opaque QR Tokens\n"
        "4. AI Chest X-ray Pneumonia Triage Screening\n"
        "5. Medical Report Summarizer & Clinical Entity Extractor\n\n"
        f"**Prototype Notice:** {GENERAL_DISCLAIMER}"
    ),
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(blood_router, prefix=API_V1_PREFIX)
app.include_router(transplant_router, prefix=API_V1_PREFIX)
app.include_router(patient_router, prefix=API_V1_PREFIX)
app.include_router(xray_router, prefix=API_V1_PREFIX)
app.include_router(report_router, prefix=API_V1_PREFIX)


@app.get("/", summary="Root Welcome")
def root_welcome():
    return JSONResponse(content={
        "service": "MEDIX Healthcare Prototype API",
        "tagline": "Connecting Care. Saving Lives.",
        "version": "2.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "disclaimer": GENERAL_DISCLAIMER
    })
