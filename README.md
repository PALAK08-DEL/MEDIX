# MEDIX — Connecting Care. Saving Lives.

**MEDIX** is a student-built healthcare platform designed to bring essential medical services and emergency information together in one place. It aims to improve access to medical resources, simplify patient information sharing, and support faster healthcare assistance through technology.

## 🚀 Problem Statement

Healthcare information and essential medical services are often scattered across different platforms. During emergencies, people may struggle to find blood availability, nearby medical facilities, or important patient information quickly.

MEDIX aims to address these challenges through a centralized digital healthcare platform.

## 💡 Our Solution

MEDIX provides a single platform that brings together important healthcare features, helping users access medical information and services more conveniently.

## ✨ Key Features

- **🩸 Blood Availability Finder** — Helps users search for blood availability using relevant blood groups and locations.
- **🫀 Organ Donation & Transplant Centre** — Provides information about organ donation and transplant-related resources.
- **📱 Patient Medical Information with QR Code** — Enables quick access to authorized patient medical information through QR codes.
- **🩻 AI Chest X-ray Pneumonia Detection** — Designed to support pneumonia screening from chest X-ray images using an AI model.
- **📄 Medical Report Summarizer** — Helps simplify complex medical reports into easier-to-understand summaries.

## 🎯 Objectives

- Centralize essential healthcare information.
- Improve access to relevant medical resources.
- Support quicker access to patient information during emergencies.
- Explore AI-based tools for healthcare assistance.
- Build a user-friendly and accessible digital healthcare experience.

## 🛠️ Technology Stack

The project uses a web-based frontend and backend architecture. The exact technologies and integrations are documented in the respective project folders.

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **Database:** SQLite
- **API Documentation:** FastAPI Swagger UI
- **QR Code:** QR code generation and scanning workflow
- **AI:** Planned/configurable chest X-ray analysis model

## 🏗️ Project Structure

```text
MEDIX/
└── medix-prototype/
    ├── frontend/
    │   ├── index.html
    │   ├── css/
    │   └── js/
    ├── backend/
    │   ├── app/
    │   ├── tests/
    │   └── requirements.txt
    ├── README.md
    └── start.sh
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or a compatible version
- A modern web browser
- A terminal or command-line interface

### Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/PALAK08-DEL/MEDIX.git
   ```

2. Open the project directory:

   ```bash
   cd MEDIX/medix-prototype
   ```

3. Follow the setup instructions in the prototype's README file.

4. Start the application using the provided startup script, if available:

   ```bash
   ./start.sh
   ```

5. Open the frontend at `http://localhost:3001`.

6. Access the backend API documentation at `http://127.0.0.1:8000/docs`.

## 🔒 Privacy & Security

MEDIX is a prototype intended for educational and demonstration purposes. Patient information should be handled carefully, and access to medical records should be restricted to authorized users. Do not upload real patient data, passwords, API keys, or other sensitive information to this repository.

## ⚠️ Disclaimer

MEDIX is a student-built prototype and is **not a substitute for professional medical advice, diagnosis, or treatment**. AI-based analysis must not be relied upon for clinical decisions. Features requiring an AI model or external services may need additional configuration before they can operate fully.

## 🔮 Future Scope

- Integration with verified healthcare providers and blood banks.
- Secure patient authentication and access controls.
- Real-time availability updates.
- Integration of a validated AI model for chest X-ray analysis.
- Improved accessibility and multilingual support.
- Deployment on a secure, scalable cloud platform.

## 👩‍💻 Project Information

**Project Name:** MEDIX  
**Tagline:** Connecting Care. Saving Lives.  
**Project Type:** Healthcare Technology / Hackathon Prototype

## 📜 License

A license has not yet been specified. Add an appropriate open-source license before permitting others to reuse or distribute this project.
