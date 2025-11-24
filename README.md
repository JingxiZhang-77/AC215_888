# AC215 - Milestone4

## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang

## Group Name
AC215_888

## Project Goal
Design and build a web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI methodology.


## Milestone 4

In Milestone 4, we combined the backend, frontend, and supporting services into a complete, locally testable system and prepared the entire application to run reliably and be packaged for future deployment.


### Data Versioning and Reproducibility

To ensure reproducibility and maintainability, we will implement a snapshot-based data versioning workflow tailored to hospital policy documents. All policy files used in retrieval (RAG), classification prompts, and decision logic are stored as timestamped snapshots in a Google Cloud Storage bucket.

This approach fits our project because hospital policies are mostly static but may undergo major updates. Snapshot-based versioning allows us to:

1. preserve historical policy states for auditing,

2. reproduce earlier model outputs, and

3. understand how policy revisions impact classification behavior.

Snapshot naming scheme:

```
policies_v1/   # initial policy set
policies_v2/   # updated discharge rules
policies_v3/   # new safety reporting guidelines
```

Reproducing a past version:

```
gsutil cp -r gs://ac215-888-artifacts/policies_v2/ data/policies/
```

Our policy documents evolve infrequently and in large, discrete updates (a static-to-semi-static dataset), making snapshot-based versioning more appropriate than diff-based tools; this ensures that every model run is tied to an exact policy version, supporting full reproducibility across time.


### Model Training or Fine-Tuning

Our current system relies on prompt engineering and RAG for safety-event classification. Prompts encode our decision logic and incorporate relevant hospital policy excerpts. This approach enables rapid iteration, strong interpretability, and avoids the computational overhead of model training.

In future iterations, we plan to explore:

- Supervised fine-tuning using labeled safety-event datasets

- Parameter-efficient fine-tuning (e.g., LoRA) for hospital-specific reasoning

- Comparisons between fine-tuned models and current prompt-based workflows, focusing on:

  - Accuracy

  - Robustness to policy updates

  - Reproducibility under versioned datasets

  - Cost and compute considerations

All datasets, prompts, and configuration files will continue to be versioned to ensure fully reproducible evaluation.


## Quick Start Guide

### Prerequisites
- Docker and Docker Compose installed
- Google Cloud Platform account with credentials
- Service account key file: `secrets/llm-service-account.json`

### Environment Setup
1. Ensure your GCP credentials are in place:
   ```bash
   ls secrets/llm-service-account.json
   ```

2. Set required environment variables (already configured in docker-shell.sh scripts):
   ```bash
   export GCP_PROJECT="apcomp215-group88"
   export GCP_REGION="us-central1"
   export GOOGLE_APPLICATION_CREDENTIALS="/secrets/llm-service-account.json"
   ```

### Starting All Services

#### Option 1: First-Time Setup (with RAG)
If you want to use the RAG (Retrieval-Augmented Generation) feature with policy documents:

**Terminal 1 - Vector Database & ChromaDB:**
```bash
cd src/vector-db
./docker-shell.sh

# Inside container - process policy documents (one-time setup):
python cli.py --chunk --chunk_type char-split
python cli.py --embed --chunk_type char-split
python cli.py --load --chunk_type char-split

# Exit container after loading
exit

# Keep ChromaDB running in background:
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

#### Option 2: Quick Start (without RAG)
If you don't need policy retrieval, skip the vector-db setup:

**Terminal 1 - API Backend:**
```bash
cd src/api
./docker-shell.sh

# Inside container:
uvicorn_server
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend-react
./docker-shell.sh

# Inside container:
npm install  # First time only
npm run dev
```

### Accessing the Application

- **Frontend UI**: http://localhost:3001
- **API Documentation**: http://localhost:9000/api/docs
- **API Health Check**: http://localhost:9000/api/v1/health
- **ChromaDB** (if running): http://localhost:8000

### Default Login Credentials

```
Username: admin
Password: admin123
```

### Supported Features

1. **Safety Event Classification**
   - 3-step classification process (GAPS, Patient Reach, Harm)
   - AI-powered decision rationales
   - Department-specific analysis

2. **Translation Support**
   - Simplified Chinese (zh-CN)
   - Traditional Chinese (zh-TW)
   - Spanish (es)
   - French (fr)
   - Auto-detection and translation to English

3. **Audio Transcription**
   - Multi-language support
   - Auto-translation to English
   - Direct classification from audio

4. **Batch Processing**
   - CSV/Excel file upload
   - Bulk incident classification
   - Export results

5. **RAG Integration** (Optional)
   - Department-specific policy retrieval
   - Enhanced classification with policy context
   - 5 departments supported:
     - Internal Medicine
     - Surgery
     - OB/GYN/NICU
     - Radiology/Imaging
     - Outpatient/ER

### Troubleshooting

**Frontend ChunkLoadError:**
If you see chunk loading errors:
```bash
cd src/frontend-react
rm -rf .next node_modules
npm install
npm run dev
```

**API Connection Issues:**
Verify services are running:
```bash
# Check API
curl http://localhost:9000/api/v1/health

# Check ChromaDB (if using RAG)
curl http://localhost:8000/api/v1/heartbeat
```

**Authentication Issues:**
If login fails, rebuild the API container:
```bash
cd src/api
docker build -t safety-event-api -f Dockerfile .
./docker-shell.sh
```

### Stopping Services

Stop all containers:
```bash
# In each terminal, press Ctrl+C to stop the service

# Stop ChromaDB if running in background:
cd src/vector-db
docker-compose down
```

### Project Structure

```
AC215_888/
├── src/
│   ├── api/              # FastAPI backend
│   ├── frontend-react/   # Next.js frontend
│   ├── vector-db/        # RAG service & ChromaDB
│   └── datapipeline/     # Data processing (not needed for demo)
├── secrets/              # GCP credentials
├── docs/                 # Documentation
└── README.md            # This file
```

### Next Steps

For detailed service documentation:
- API: See `src/api/README.md`
- Frontend: See `src/frontend-react/README.md`
- RAG: See `src/vector-db/README.md`


