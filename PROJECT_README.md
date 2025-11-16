# Safety Event Classification System

**Team:** AC215_888  
**Members:** Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang  
**Version:** 1.0.0

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Features](#features)
- [Quick Start](#quick-start)
- [Services](#services)
- [Development Guidelines](#development-guidelines)
- [API Documentation](#api-documentation)
- [Testing](#testing)

---

## 🎯 Project Overview

A comprehensive AI-powered system for classifying healthcare safety incidents using Large Language Models (LLMs). The system provides:

- **Multi-language audio transcription** with automatic translation
- **Three-step classification** process with transparent rationales
- **Department-based tracking** across 5 medical departments
- **REST API backend** with role-based access control
- **Web interface** for incident submission and analysis
- **Batch processing** for CSV/Excel files

### Classification Methodology

Following the Hospital Patient Incident (HPI) methodology:

1. **GAPS Deviation Check**: Identify deviations from Generally Accepted Performance Standards
2. **Patient Reach Assessment**: Determine if incident reached the patient
3. **Harm Level Evaluation**: Assess actual patient harm

**Classification Codes:**
- `NSE`: No Safety Event (no deviation detected)
- `NME`: No Medical Event (deviation didn't reach patient)
- `NHE`: No Harm Event (reached patient, no harm)
- `HE`: Harmful Event (patient experienced harm)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Flask)                      │
│                   Web UI + User Interface                    │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Auth     │  │ Classification│  │    Audio     │     │
│  │   Service    │  │    Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼────────┐ ┌▼────────────┐
│  Google LLM  │ │  Google   │ │  Google     │
│   (Gemini)   │ │  Speech   │ │  Translate  │
└──────────────┘ └───────────┘ └─────────────┘
```

---

## 📁 Repository Structure

```
AC215_888/
├── README.md                          # This file
├── DEPARTMENT_FEATURE.md             # Department tracking documentation
├── DOCKER_ENTRYPOINT_SETUP.md        # Docker setup guide
│
├── src/
│   ├── api/                          # Backend REST API (FastAPI)
│   │   ├── README.md                 # API documentation
│   │   ├── main.py                   # API entry point
│   │   ├── routers/                  # API endpoints
│   │   │   ├── auth.py              # Authentication
│   │   │   ├── users.py             # User management
│   │   │   ├── classification.py    # Classification endpoints
│   │   │   └── audio.py             # Audio endpoints
│   │   ├── services/                 # Business logic
│   │   │   ├── classification_service.py
│   │   │   └── audio_service.py
│   │   ├── models/                   # Data models
│   │   │   └── schemas.py
│   │   ├── utils/                    # Utilities
│   │   │   ├── config.py
│   │   │   ├── auth.py
│   │   │   └── logger.py
│   │   ├── Dockerfile
│   │   ├── docker-shell.sh
│   │   ├── docker-entrypoint.sh
│   │   └── pyproject.toml
│   │
│   ├── frontend/                     # Web interface (Flask)
│   │   ├── README.md
│   │   ├── app.py                    # Flask application
│   │   ├── templates/                # HTML templates
│   │   ├── static/                   # CSS, JavaScript
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── model/                        # LLM classification logic
│   │   ├── safety_event_classifier.py
│   │   ├── simple_prompt_utils.py
│   │   ├── prompt_utils.py
│   │   ├── Dockerfile
│   │   └── docker-shell.sh
│   │
│   ├── audio-service/                # Audio transcription
│   │   ├── audio_transcriber.py
│   │   ├── Dockerfile
│   │   └── docker-shell.sh
│   │
│   └── datapipeline/                 # Data generation
│       ├── data_generation.py
│       ├── Dockerfile
│       └── docker-shell.sh
│
├── secrets/                          # GCP credentials (gitignored)
│   └── llm-service-account.json
│
├── reports/                          # Project reports and presentations
│   └── Milestone3_Presentation.pdf
│
└── references/                       # Lecture tutorials and examples
    └── lecture_tutorials/
```

---

## ✨ Features

### 🔐 Authentication & Authorization
- JWT token-based authentication
- 4 user roles: Admin, Doctor, Nurse, Viewer
- Password reset functionality
- Role-based endpoint access control

### 🎤 Multi-Language Audio Support
- **Supported Languages**: English, Mandarin, Cantonese, French, Spanish
- **Audio Formats**: MP3, WAV, M4A, FLAC, OGG
- **Automatic Translation**: Non-English audio translated to English
- **Medical Terminology**: Optimized for healthcare vocabulary

### 🤖 AI-Powered Classification
- **Three-Step Process**: GAPS → Patient Reach → Harm Level
- **Transparent Rationales**: AI explains each decision
- **Department Tracking**: 5 medical departments
- **Batch Processing**: CSV/Excel file uploads

### 🏥 Department Categories
1. Internal Medicine
2. Surgery
3. OB/GYN/NICU
4. Radiology/Imaging
5. Outpatient/ER

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (required)
- **Google Cloud credentials**: `secrets/llm-service-account.json`
- **Python 3.11** (for local development)

### 1. Clone Repository

```bash
git clone https://github.com/JingxiZhang-77/AC215_888.git
cd AC215_888
```

### 2. Setup Credentials

Place your Google Cloud service account key:
```bash
mkdir -p secrets
# Copy your llm-service-account.json to secrets/
```

### 3. Start Backend API

```bash
cd src/api
sh docker-shell.sh

# Inside container
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

API will be available at: http://localhost:9000

### 4. Start Frontend (Optional)

```bash
cd src/frontend
sh docker-shell.sh

# Inside container
python app.py
```

Frontend will be available at: http://localhost:5000

### 5. Test API

```bash
# Health check
curl http://localhost:9000/api/health

# View API documentation
open http://localhost:9000/api/docs
```

---

## 🔧 Services

### 1. Backend API (`src/api/`)

**FastAPI REST API** providing all backend functionality.

**Key Features:**
- JWT authentication
- Multi-language audio transcription
- Classification with rationales
- User management
- Batch processing

**Documentation:** [src/api/README.md](src/api/README.md)

**Endpoints:**
- `/api/v1/auth/*` - Authentication
- `/api/v1/users/*` - User management
- `/api/v1/classify/*` - Classification
- `/api/v1/audio/*` - Audio transcription

**Start Service:**
```bash
cd src/api
sh docker-shell.sh
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 2. Frontend (`src/frontend/`)

**Flask web application** for user interface.

**Features:**
- User registration/login
- Single incident classification
- Batch file upload
- Results with rationales
- Department selection

**Start Service:**
```bash
cd src/frontend
sh docker-shell.sh
python app.py
```

### 3. Model Service (`src/model/`)

**LLM-based classification** logic using Google Gemini.

**Features:**
- Three-step prompting
- Rationale generation
- Batch processing CLI
- Department tracking

**Usage:**
```bash
cd src/model
sh docker-shell.sh
python safety_event_classifier.py -f incidents.csv -d "surgery"
```

### 4. Audio Service (`src/audio-service/`)

**Standalone audio transcription** service.

**Features:**
- Google Speech-to-Text API
- Medical dictation model
- Multi-language support

**Usage:**
```bash
cd src/audio-service
sh docker-shell.sh
python audio_transcriber.py audio_file.mp3 --language en-US
```

### 5. Data Pipeline (`src/datapipeline/`)

**Synthetic data generation** for training/testing.

**Usage:**
```bash
cd src/datapipeline
sh docker-shell.sh
python data_generation.py --generate 100
```

---

## 📖 Development Guidelines

### Code Style

**Python (PEP 8):**
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Comprehensive docstrings for all functions/classes
- Type hints for function parameters and returns

**Directory Organization:**
- `api/` - API layer (routers)
- `services/` - Business logic
- `models/` - Data models (Pydantic)
- `utils/` - Utilities and helpers
- `tests/` - Unit and integration tests

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Update models**: Add Pydantic schemas in `models/schemas.py`
3. **Implement service**: Add business logic in `services/`
4. **Create router**: Add endpoints in `routers/`
5. **Register router**: Update `main.py`
6. **Write tests**: Add tests in `tests/`
7. **Document**: Update README and add docstrings

### Environment Variables

Create `.env` file:
```bash
# Google Cloud
GCP_PROJECT=apcomp215-group88
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json

# API
PORT=9000
DEBUG=true
SECRET_KEY=your-secret-key

# LLM
LLM_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.2
```

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:9000/api/docs
- **ReDoc**: http://localhost:9000/api/redoc

### Example: Classify Incident

```bash
# 1. Login
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Classify Incident
curl -X POST http://localhost:9000/api/v1/classify/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Patient fell while walking to bathroom",
    "department": "internal medicine"
  }'
```

### Example: Audio Classification

```bash
curl -X POST http://localhost:9000/api/v1/classify/audio \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@incident.mp3" \
  -F "language=zh-CN" \
  -F "department=surgery" \
  -F "auto_translate=true"
```

**Full API Documentation:** [src/api/README.md](src/api/README.md)

---

## 🧪 Testing

### Unit Tests

```bash
cd src/api
pytest tests/
```

### Integration Tests

```bash
pytest tests/integration/
```

### Manual Testing

Use Swagger UI at http://localhost:9000/api/docs

---

## 📊 Project Milestones

### ✅ Milestone 1
- Project planning and architecture design

### ✅ Milestone 2
- Data generation pipeline
- Basic classification model
- Initial evaluation

### ✅ Milestone 3
- Presentation and project consolidation
- Documentation and visualizations

### ✅ Current Milestone
- ✅ Department tracking feature
- ✅ Authentication system with RBAC
- ✅ Multi-language audio support
- ✅ REST API backend
- ✅ Comprehensive documentation
- ✅ Docker containerization

---

## 🔒 Security Notes

1. **Credentials**: Never commit `secrets/` directory
2. **JWT Tokens**: Use strong secret keys in production
3. **HTTPS**: Enable in production environments
4. **Input Validation**: All inputs validated by Pydantic
5. **Password Hashing**: Bcrypt with salt

---

## 📝 License

Copyright © 2025 AC215_888 Team. All rights reserved.

---

## 🤝 Contributing

### Team Members Responsibilities

- **Zilong Wang**: Data pipeline and model training
- **Jingxi Zhang**: Classification logic and evaluation
- **Bruce Zhou**: Backend API and infrastructure
- **Alice Zhang**: Frontend and user experience

### Development Workflow

1. Create feature branch
2. Implement changes following style guide
3. Write tests
4. Update documentation
5. Submit pull request
6. Code review
7. Merge to main

---

## 📞 Support

For questions or issues:
- Check API documentation: http://localhost:9000/api/docs
- Review service-specific READMEs
- Contact team members

---

## 🎓 Acknowledgments

- **Harvard AC215**: Applied Computer Science class
- **Google Cloud Platform**: LLM and audio services
- **FastAPI Framework**: Backend API development
- **Flask Framework**: Web interface

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Status:** Production Ready
