# Safety Event Classification API

**Version:** 1.0.0  
**Framework:** FastAPI + Python 3.11  
**Purpose:** REST API backend for AI-powered safety event classification with multi-language audio transcription

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)

---

## 🎯 Overview

The Safety Event Classification API provides a comprehensive backend service for analyzing and classifying healthcare safety incidents using AI-powered decision-making with transparent rationales. The system supports multi-language audio input, automatic translation, and department-based tracking.

### Key Capabilities

- **AI Classification**: Three-step classification process (GAPS deviation → Patient reach → Harm level)
- **Multi-Language Audio**: Transcription in English, Mandarin, Cantonese, French, Spanish
- **Auto-Translation**: Non-English transcripts automatically translated to English
- **Batch Processing**: Upload CSV/Excel files for bulk classification
- **Role-Based Access**: JWT authentication with 4 user roles
- **Department Tracking**: 5 medical department categories
- **Comprehensive Rationales**: AI-generated explanations for each decision

---

## ✨ Features

### 🔐 Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- Password reset + token verification
- Roles: Admin, Doctor, Nurse, Viewer

### 🎤 Audio Transcription
- **Supported Languages**:
  - 🇺🇸 English (en-US)
  - 🇨🇳 Mandarin/Simplified Chinese (zh-CN)
  - 🇭🇰 Cantonese (zh-HK)
  - 🇫🇷 French (fr-FR)
  - 🇪🇸 Spanish (es-ES)
- **Audio Formats**: MP3, WAV, M4A, FLAC, OGG
- **Medical Dictation Model**: Optimized for healthcare terminology
- **Automatic Translation**: Non-English → English

### 🏥 Classification System
- **GAPS Deviation Check**: Identifies deviations from Generally Accepted Performance Standards
- **Patient Reach Assessment**: Determines if incident reached patient
- **Harm Level Evaluation**: Assesses actual patient harm
- **Gemini Integration**: Each step calls Google Cloud Vertex AI (Gemini 2.5) through the shared `src/model/simple_prompt_utils.py` helpers for consistent reasoning
- **Department Normalization**: Accepts both slugged (`internal_medicine`) and human-readable (`Internal Medicine`) department inputs and normalizes them before classification
- **Classification Codes** (ranked by descending level of seriousness):
  - `SSE`: Serious Safety Event (moderate/severe harm or death)
  - `PSE`: Precursor Safety Event (reached patient, no/minimal harm)
  - `NME`: Near Miss Event (deviation didn't reach patient)
  - `NSE`: No Safety Event (no deviation from GAPS)

### 🏢 Department Tracking
- Internal Medicine
- Surgery
- OB/GYN/NICU
- Radiology/Imaging
- Outpatient/ER

### 📁 Batch Processing
- Upload CSV or Excel files that contain at least `description` and (optionally normalized) `department` columns
- Departments can be provided with spaces, underscores, or mixed casing—the backend normalizes them before invoking Gemini
- A starter template is included in `src/frontend-react/public/batch-template.csv` for quick testing

---

## 🏗️ Architecture

```
src/api/
├── main.py                    # FastAPI application entry point
├── routers/                   # API endpoint definitions
│   ├── auth.py               # Authentication endpoints
│   ├── users.py              # User management (admin)
│   ├── classification.py     # Classification endpoints
│   └── audio.py              # Audio transcription endpoints
├── services/                  # Business logic layer
│   ├── classification_service.py  # Classification logic
│   └── audio_service.py      # Audio transcription & translation
├── models/                    # Data models (Pydantic)
│   └── schemas.py            # Request/response schemas
├── utils/                     # Utility functions
│   ├── config.py             # Configuration management
│   ├── logger.py             # Logging setup
│   └── auth.py               # JWT authentication utilities
├── pyproject.toml            # Dependencies
├── Dockerfile                # Container image definition
├── docker-shell.sh           # Build and run script
└── docker-entrypoint.sh      # Container initialization
```

### Design Patterns

- **Separation of Concerns**: Routers → Services → Utils
- **Dependency Injection**: FastAPI's `Depends()` for auth
- **Repository Pattern**: Service layer abstracts business logic
- **Factory Pattern**: Configuration and logger setup

---

## 🚀 Setup Instructions

### Prerequisites

- **Docker** (recommended) OR Python 3.11
- **Google Cloud credentials** (for LLM and audio services)
- **Secrets**: `secrets/llm-service-account.json`

### Test Account

To keep the MVP workflow predictable, only a single administrative account is shipped with the backend:

| Username | Password | Role | Department | Scope |
|----------|----------|------|------------|-------|
| `admin` | `admin123` | Admin | Internal Medicine | Access to every feature |

> Registration endpoints are disabled for now. Use the admin credentials above to exercise the system end‑to‑end.

### Option 1: Docker (Recommended)

```bash
# From the repository root (AC215_888)
sh src/api/docker-shell.sh

# Inside the container shell, install secrets (if needed) and start the server
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

This script now builds the API image **from the repo root** so that `src/model/simple_prompt_utils.py`
and other shared assets are copied into the container. If you see the message
`Warning: simple_prompt_utils not available`, rebuild using this script and ensure the secrets
volume (`/secrets/llm-service-account.json`) is mounted.

**Verify Installation:**
```bash
# Check API health
curl http://localhost:9000/api/health

# Test login with admin account
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Option 2: Local Development (Alternative)

```bash
# Navigate to API directory
cd src/api

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r pyproject.toml

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS=../../secrets/llm-service-account.json
export GCP_PROJECT=apcomp215-group88
export GCP_REGION=us-central1

# Run API server
python main.py
```

### Verify Installation

```bash
# Check API health
curl http://localhost:9000/api/health

# Open interactive documentation
open http://localhost:9000/api/docs
```

---

## 📚 API Endpoints

### Base URL
```
http://localhost:9000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:9000/api/docs
- **ReDoc**: http://localhost:9000/api/redoc

### Endpoint Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| **Authentication** ||||
| POST | `/api/v1/auth/login` | User login (get JWT) | No |
| POST | `/api/v1/auth/forgot-password` | Request password reset | No |
| POST | `/api/v1/auth/reset-password` | Reset password with token | No |
| GET | `/api/v1/auth/verify` | Verify JWT token | Yes |
| **User Management** ||||
| GET | `/api/v1/users/` | List all users | Admin |
| GET | `/api/v1/users/{username}` | Get user details | Admin |
| PATCH | `/api/v1/users/{username}` | Update user | Admin |
| DELETE | `/api/v1/users/{username}` | Delete user | Admin |
| GET | `/api/v1/users/me` | Get current user | User |
| **Classification** ||||
| POST | `/api/v1/classify/` | Classify single incident | Doctor/Nurse/Admin |
| POST | `/api/v1/classify/batch` | Classify from file (CSV/Excel) | Doctor/Nurse/Admin |
| POST | `/api/v1/classify/audio` | Transcribe + classify audio | Doctor/Nurse/Admin |
| **Audio** ||||
| POST | `/api/v1/audio/transcribe` | Transcribe audio only | Doctor/Nurse/Admin |
| GET | `/api/v1/audio/languages` | List supported languages | Public |

---

## 🔐 Authentication

### Registration

User self-registration is intentionally disabled in this MVP build so that the single admin account remains the only way to access protected features during testing. Re‑enable `/auth/register` only when you are ready to support additional accounts.

### Login

```bash
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "username": "jdoe",
    "email": "jdoe@hospital.com",
    "role": "doctor"
  }
}
```

### Using JWT Token

Include token in `Authorization` header:

```bash
curl -X POST http://localhost:9000/api/v1/classify/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Patient fell"}'
```

---

## 💡 Usage Examples

### 1. Classify Single Incident

```bash
curl -X POST http://localhost:9000/api/v1/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Patient fell in hallway while walking to bathroom",
    "department": "internal medicine"
  }'
```

Response:
```json
{
  "incident": "Patient fell in hallway...",
  "department": "internal medicine",
  "department_label": "Internal Medicine",
  "department_slug": "internal_medicine",
  "deviation_check": "Yes",
  "deviation_rationale": "Environmental hazards and lack of escort indicate deviation from fall protocols.",
  "patient_reach_check": "Yes",
  "patient_reach_rationale": "The patient directly experienced the fall event.",
  "harm_level_check": "No",
  "harm_level_rationale": "Only mild bruising reported; no further intervention required.",
  "classification_code": "PSE",
  "classification_label": "Precursor Safety Event",
  "classification_rationale": "Deviation reached the patient but caused only minimal harm.",
  "status": "success",
  "timestamp": "2025-01-15T10:30:00Z",
  "gaps_deviation_check": "Yes",
  "gaps_rationale": "Environmental hazards and lack of escort indicate deviation from fall protocols.",
  "reached_patient_check": "Yes",
  "reached_patient_rationale": "The patient directly experienced the fall event.",
  "final_classification_code": "PSE",
  "final_rationale": "Deviation reached the patient but caused only minimal harm."
}
```
> The `classification_*` fields are the canonical outputs. Legacy fields such as `final_classification_code` remain for backward compatibility.

## ⚙️ Troubleshooting

- **Seeing “Mock rationale – prompt utils not available”**  
  The API fell back to the mock classifier because it could not import `src/model/simple_prompt_utils.py`. Rebuild the Docker image from the **repo root** using `sh src/api/docker-shell.sh` (this copies `src/model` into the container) or, for local dev, run the server from the repo so `src/model` stays on `PYTHONPATH`. Also verify that `google-genai` is installed (`pip install -r pyproject.toml`) and that `GOOGLE_APPLICATION_CREDENTIALS`, `GCP_PROJECT`, and `GCP_REGION` are set.
- **Credentials warning in entrypoint**  
  Make sure `secrets/llm-service-account.json` exists and is mounted into the container (`/secrets`). The entrypoint prints a warning if the file is missing.

### 2. Batch Classification (CSV)

```bash
curl -X POST http://localhost:9000/api/v1/classify/batch \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@incidents.csv"
```

CSV Format:
```csv
Description,Department
Patient fell in hallway,internal medicine
Wrong medication dose administered,surgery
Equipment malfunction in OR,surgery
```

### 3. Audio Transcription + Classification

```bash
curl -X POST http://localhost:9000/api/v1/classify/audio \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@incident_recording.mp3" \
  -F "language=en-US" \
  -F "department=surgery" \
  -F "auto_translate=true"
```

Response:
```json
{
  "transcription": {
    "transcript": "There was a near miss with medication...",
    "original_language": "English",
    "was_translated": false,
    "confidence": 0.95,
    "duration_seconds": 15.3
  },
  "classification": {
    "incident": "There was a near miss...",
    "department": "surgery",
    "final_classification_code": "NME",
    ...
  },
  "processing_time": 3.2
}
```

### 4. Audio Transcription Only (Mandarin)

```bash
curl -X POST http://localhost:9000/api/v1/audio/transcribe \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@chinese_recording.mp3" \
  -F "language=zh-CN" \
  -F "auto_translate=true"
```

Response:
```json
{
  "transcript": "There was a medication error during surgery...",
  "original_language": "Mandarin (Simplified)",
  "was_translated": true,
  "confidence": 0.92,
  "duration_seconds": 22.1
}
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file or set environment variables:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
PORT=9000

# Google Cloud
GCP_PROJECT=apcomp215-group88
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# LLM
LLM_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=1000

# File Upload
MAX_UPLOAD_SIZE_MB=25
AUDIO_MAX_FILE_SIZE_MB=50
```

### Configuration File

Edit `src/api/utils/config.py` to modify default settings.

---

## 🛠️ Development

### Code Style

Follow **PEP 8** style guide:

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Project Structure Rules

1. **Routers**: Only endpoint definitions, delegate to services
2. **Services**: Business logic, no HTTP concerns
3. **Models**: Pydantic schemas for validation
4. **Utils**: Reusable utilities (auth, config, logging)

### Adding New Endpoints

1. Create router in `routers/`
2. Define Pydantic models in `models/schemas.py`
3. Implement business logic in `services/`
4. Register router in `main.py`

Example:
```python
# routers/analytics.py
from fastapi import APIRouter, Depends
from utils.auth import require_role

router = APIRouter()

@router.get("/stats")
async def get_stats(user = Depends(require_role("admin"))):
    return {"total_incidents": 1234}

# main.py
from routers import analytics
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
```

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
uv pip install pytest httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Manual Testing with cURL

See [Usage Examples](#usage-examples) section.

### Testing with Swagger UI

1. Navigate to http://localhost:9000/api/docs
2. Click "Authorize" button
3. Login to get JWT token
4. Enter token: `Bearer YOUR_TOKEN`
5. Test endpoints interactively

---

## 📊 API Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (registration) |
| 204 | No Content (deletion) |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 413 | Payload Too Large |
| 500 | Internal Server Error |

---

## 🔒 Security Considerations

1. **JWT Tokens**: Store securely, include in Authorization header
2. **HTTPS**: Use in production (not implemented in dev)
3. **Secret Key**: Change default `SECRET_KEY` in production
4. **Rate Limiting**: Implement in production
5. **Input Validation**: All inputs validated by Pydantic
6. **Password Hashing**: Bcrypt with salt

---

## 📝 License

Copyright © 2025 AC215_888 Team. All rights reserved.

---

## 🤝 Support

For issues or questions:
- Check API documentation: http://localhost:9000/api/docs
- Review logs in container
- Contact: AC215_888 Team

---

## 📅 Changelog

### Version 1.0.0 (2025-01-15)
- Initial release
- JWT authentication with RBAC
- Multi-language audio transcription (5 languages)
- Automatic translation to English
- Three-step classification system with rationales
- Batch processing from CSV/Excel
- Department tracking (5 departments)
- Comprehensive API documentation
