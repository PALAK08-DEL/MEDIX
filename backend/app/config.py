"""
MEDIX Prototype Backend — Central Configuration Settings
"""

import os
from typing import List

HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "medix.db")
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# CORS Origins for local web dev
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "*"
]

API_V1_PREFIX: str = "/api/v1"

# Upload limits
MAX_XRAY_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAX_REPORT_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
SUPPORTED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
SUPPORTED_REPORT_TYPES: List[str] = ["text/plain", "application/pdf"]

# Standard blood groups
VALID_BLOOD_GROUPS: List[str] = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Optional AI external configurations
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
XRAY_MODEL_PATH: str = os.getenv("XRAY_MODEL_PATH", "")

# Prototype Disclaimers
GENERAL_DISCLAIMER: str = (
    "MEDIX is a student healthcare hackathon prototype. All records, hospital contacts, "
    "inventory metrics, and doctor entries are simulated demonstration data. "
    "Not connected to real hospital databases, clinical records, or live municipal 911 dispatch."
)

BLOOD_DISCLAIMER: str = (
    "DEMONSTRATION ONLY: All blood bank inventories, distances, and contact numbers are fictional demo data. "
    "Reservations and pledges are simulated and do not dispatch actual blood products."
)

TRANSPLANT_DISCLAIMER: str = (
    "AWARENESS & EDUCATION ONLY: Fictional demonstration directory. "
    "No actual organ allocation, waitlist priority, or recipient matching is performed."
)

QR_DISCLAIMER: str = (
    "PROTOTYPE DEMONSTRATION: Patient records are synthetic demo profiles. "
    "Do not input real personal identifiable health information (PHI). "
    "Opaque tokens resolve safely without exposing full history in raw QR codes."
)

XRAY_DISCLAIMER: str = (
    "INVESTIGATIONAL PROTOTYPE: Not certified for clinical diagnosis. "
    "AI chest radiograph analysis must be validated by licensed radiologists."
)

REPORT_DISCLAIMER: str = (
    "INFORMATIONAL EXTRACTOR: Not a substitute for professional medical review. "
    "Always consult qualified clinicians for diagnostic conclusions."
)
