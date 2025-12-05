# AC215 - Hospital Safety Event Classification System

## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang

## Group Name
AC215_888

## Project Overview

A web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI (Healthcare Performance Improvement) methodology.

### Key Features
- **3-Step Classification**: GAPS analysis, Patient Reach, and Harm assessment
- **Multi-language Support**: Chinese (Simplified/Traditional), Spanish, French with auto-translation
- **Audio Transcription**: Voice-to-text incident reporting
- **Batch Processing**: CSV/Excel file upload for bulk classification
- **RAG Integration**: Department-specific policy retrieval for enhanced accuracy
- **Auto-scaling**: Kubernetes deployment with horizontal pod autoscaling

---

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Quick Start (Local Development)](#quick-start-local-development)
4. [Production Deployment](#production-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Testing](#testing)
7. [Evaluation](#evaluation)
8. [Data Pipeline](#data-pipeline)
9. [Infrastructure as Code](#infrastructure-as-code)
10. [Frontend UI Preview](#frontend-ui-preview)

---

## Architecture

<img width="591" height="331" alt="Architecture Overview" src="https://github.com/user-attachments/assets/de02f3d4-2ac6-43cb-999d-e83e158bf457" />

<img width="589" height="333" alt="System Components" src="https://github.com/user-attachments/assets/d52387e2-8f31-49f0-9272-c62bc646ee53" />

### Components
| Component | Technology | Description |
|-----------|------------|-------------|
| Frontend | Next.js 15, React, TailwindCSS | Modern responsive UI |
| API Backend | FastAPI, Python 3.11 | RESTful API with OpenAPI docs |
| LLM | Google Gemini 2.5 Flash (Vertex AI) | Classification engine |
| Vector Database | ChromaDB | Policy document retrieval (RAG) |
| Container Runtime | Docker | Consistent development environment |
| Orchestration | Kubernetes (GKE) | Production deployment |
| IaC | Pulumi (Python) | Infrastructure automation |

---

## Project Structure

```
AC215_888/
├── src/                          # Source code
│   ├── api/                      # FastAPI backend service
│   │   ├── model/                # ML classification logic
│   │   ├── models/               # Pydantic data schemas
│   │   ├── routers/              # API route handlers
│   │   ├── services/             # Business logic services
│   │   ├── utils/                # Utility functions
│   │   ├── Dockerfile
│   │   └── docker-shell.sh
│   ├── frontend-react/           # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/              # App router pages
│   │   │   └── components/       # React components
│   │   ├── Dockerfile
│   │   └── docker-shell.sh
│   ├── vector-db/                # RAG service & ChromaDB
│   │   ├── cli.py                # Vector DB management CLI
│   │   ├── docker-compose.yml
│   │   └── docker-shell.sh
│   └── data-pipeline/            # Synthetic data generation
│       ├── data_generation.py
│       ├── Dockerfile
│       └── docker-shell.sh
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── system/                   # End-to-end tests
├── evaluation/                   # Model evaluation pipeline
│   ├── evaluate.py
│   ├── Dockerfile
│   └── docker-shell.sh
├── k8s/                          # Kubernetes manifests
│   ├── api-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── chromadb-statefulset.yaml
│   ├── hpa.yaml                  # Auto-scaling config
│   └── deploy.sh
├── deployment/                   # Additional deployment configs
├── secrets/                      # GCP credentials (gitignored)
├── .github/workflows/            # CI/CD pipelines
├── Dockerfile.test               # Test container
└── pytest.ini                    # Test configuration
```

---

## Quick Start (Local Development)

### Prerequisites
- Docker and Docker Compose
- GCP service account key: `secrets/llm-service-account.json`

### Option 1: Full Stack (with RAG)

**Terminal 1 - Vector Database:**
```bash
cd src/vector-db
./docker-shell.sh

# Inside container - one-time setup:
python cli.py --chunk --chunk_type char-split
python cli.py --embed --chunk_type char-split
python cli.py --load --chunk_type char-split
exit

# Keep ChromaDB running:
docker-compose up -d chromadb
```

**Terminal 2 - API Backend:**
```bash
cd src/api
./docker-shell.sh
# Inside container:
uvicorn_server
```

**Terminal 3 - Frontend:**
```bash
cd src/frontend-react
./docker-shell.sh
# Inside container:
npm install  # First time only
npm run dev
```

### Option 2: Quick Start (without RAG)

**Terminal 1 - API:**
```bash
cd src/api && ./docker-shell.sh
# Inside: uvicorn_server
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend-react && ./docker-shell.sh
# Inside: npm install && npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3001 |
| API Docs | http://localhost:9000/api/docs |
| Health Check | http://localhost:9000/api/v1/health |
| ChromaDB | http://localhost:8000 |

**Default Login:** `admin` / `admin123`

---

## Production Deployment

### Live System (GKE)

Our application is deployed on Google Kubernetes Engine:

| Service | URL |
|---------|-----|
| Frontend | http://34.136.237.225 |
| API Docs | http://136.111.94.120:9000/api/docs |
| Health Check | http://136.111.94.120:9000/api/v1/health |

**Credentials:** `admin` / `admin123`

### Cluster Configuration
- **Platform**: Google Kubernetes Engine (GKE)
- **Region**: us-central1
- **Nodes**: 6 × e2-standard-2
- **Namespace**: safety-event-system

### Auto-Scaling (HPA)

| Component | Min Pods | Max Pods | Scale Trigger |
|-----------|----------|----------|---------------|
| API | 3 | 10 | CPU 70%, Memory 80% |
| Frontend | 2 | 6 | CPU 70% |

### Deploy to Kubernetes

```bash
cd k8s
./deploy.sh
```

For detailed instructions, see [`k8s/README.md`](k8s/README.md).

---

## CI/CD Pipeline

GitHub Actions workflow runs on every push and PR:

### Pipeline Stages

1. **Build & Lint**
   - Docker image build
   - Black formatting check
   - Flake8 linting

2. **Test**
   - Unit tests (44 tests)
   - Integration tests (25 tests)
   - System tests (end-to-end)

3. **Coverage**
   - Minimum threshold: 50%
   - Current coverage: 91%

<img width="1630" height="472" alt="CI Pipeline" src="https://github.com/user-attachments/assets/e67a80f3-f391-4ce5-b524-7eb28f72c741" />

### Run Tests Locally

```bash
# Using Docker (recommended)
docker build -t safety-event-api:local -f Dockerfile.test .
docker run --rm safety-event-api:local pytest tests/ -v --cov

# Or using the test script
./run-tests.sh
```

---

## Testing

### Test Structure

```
tests/
├── unit/                  # Component isolation tests
│   ├── test_auth.py       # Authentication utilities
│   ├── test_config.py     # Configuration handling
│   └── test_lang.py       # Language detection
├── integration/           # API endpoint tests
│   └── test_api.py        # Full API integration
└── system/                # End-to-end workflows
    └── test_system_api.py # Complete system tests
```

### Coverage Report

| Module | Coverage |
|--------|----------|
| utils/ | 91% |
| models/ | 85% |
| routers/ | 78% |
| **Overall** | **91%** |

---

## Evaluation

The evaluation pipeline measures model classification performance.

### Run Evaluation

```bash
cd evaluation
./docker-shell.sh

# Inside container:
python evaluate.py --input_file data/test_data.xlsx --output_dir outputs/
```

### Metrics Generated
- Classification accuracy
- Per-class precision, recall, F1
- Confusion matrix visualization
- Detailed classification report

See [`evaluation/README.md`](evaluation/README.md) for details.

---

## Data Pipeline

Generate synthetic medical incident data for training and evaluation.

### Run Data Generation

```bash
cd src/data-pipeline
./docker-shell.sh

# Inside container:
python data_generation.py --num_samples 50 --output_file outputs/incidents.csv
```

### Output
- CSV/Excel with Department and Incident Description
- Raw LLM response backup

See [`src/data-pipeline/README.md`](src/data-pipeline/README.md) for details.

---

## Infrastructure as Code

### Pulumi (Python)

All infrastructure defined in code:

```bash
cd infra

# Deploy
pulumi up

# Get URLs
pulumi stack output frontend_url
pulumi stack output api_url

# Destroy
pulumi destroy
```

### What Pulumi Provisions
- GKE cluster (6 nodes, multi-zone)
- Kubernetes deployments (API, Frontend, ChromaDB)
- LoadBalancer services
- Horizontal Pod Autoscalers
- Persistent Volume Claims
- Secrets and ConfigMaps

See [`infra/README.md`](infra/README.md) for details.

---

## Frontend UI Preview

<img width="1504" height="843" alt="Login" src="https://github.com/user-attachments/assets/277a1ddf-ce4c-4597-b1ec-3865fedf418f" />

<img width="1506" height="823" alt="Classification" src="https://github.com/user-attachments/assets/9489950c-10d5-4bda-a827-cd883f5f4427" />

<img width="1484" height="855" alt="Results" src="https://github.com/user-attachments/assets/0b799647-953e-4cd0-8eac-73e11a04e1a9" />

<img width="1506" height="851" alt="Batch Processing" src="https://github.com/user-attachments/assets/0842f3d6-a4af-4879-9eeb-a3b9bee665e0" />

<img width="1500" height="844" alt="Translation" src="https://github.com/user-attachments/assets/792c13d2-d406-49d6-9b48-131bee139b5e" />

<img width="1510" height="848" alt="Audio" src="https://github.com/user-attachments/assets/fef2cb74-cf86-4c1a-9e36-1e18a5feaaeb" />

---

## Documentation

| Component | Documentation |
|-----------|---------------|
| API Backend | [`src/api/README.md`](src/api/README.md) |
| Frontend | [`src/frontend-react/README.md`](src/frontend-react/README.md) |
| Vector DB / RAG | [`src/vector-db/README.md`](src/vector-db/README.md) |
| Data Pipeline | [`src/data-pipeline/README.md`](src/data-pipeline/README.md) |
| Evaluation | [`evaluation/README.md`](evaluation/README.md) |
| Kubernetes | [`k8s/README.md`](k8s/README.md) |
| Infrastructure | [`infra/README.md`](infra/README.md) |

---

## License

This project is developed for academic purposes as part of Harvard AC215: MLOps.
