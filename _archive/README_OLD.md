# AC215 - Milestone 5

## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang

## Group Name
AC215_888

## Project Goal
Design and build a web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI methodology.

## Milestone 5 Overview

In Milestone 5, we achieved production-ready deployment and automation:

1. **Kubernetes Deployment**: Deployed the complete application to Google Kubernetes Engine (GKE) with auto-scaling capabilities
2. **Infrastructure as Code**: Implemented Pulumi to automate infrastructure provisioning and application deployment
3. **CI/CD Pipeline**: Established comprehensive GitHub Actions workflows with automated testing and deployment
4. **ML Workflow**: Integrated production-ready machine learning pipeline with data versioning and model evaluation

## Table of Contents

1. [Application Architecture](#application-design-document)
2. [Kubernetes Deployment (Production)](#kubernetes-deployment-production)
3. [Infrastructure as Code with Pulumi](#infrastructure-as-code-with-pulumi)
4. [CI/CD Pipeline](#continuous-integration-and-deployment)
5. [Machine Learning Workflow](#machine-learning-workflow)
6. [Local Development Setup](#apis-and-frontend-implementation-quick-start-guide)
7. [Frontend UI Preview](#frontend-ui-preview)

---

## Application Design Document

<img width="591" height="331" alt="Screenshot 2025-11-25 at 14 56 31" src="https://github.com/user-attachments/assets/de02f3d4-2ac6-43cb-999d-e83e158bf457" />

<img width="589" height="333" alt="Screenshot 2025-11-25 at 14 56 51" src="https://github.com/user-attachments/assets/d52387e2-8f31-49f0-9272-c62bc646ee53" />


## APIs and Frontend Implementation (Quick Start Guide)

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

---

## Kubernetes Deployment (Production)

### ✅ Live Production System

Our application is deployed on **Google Kubernetes Engine (GKE)** and is **accessible 24/7**:

- **Frontend Application**: http://34.136.237.225
- **API Documentation**: http://136.111.94.120:9000/api/docs
- **Health Check**: http://136.111.94.120:9000/api/v1/health

**Login Credentials**: `admin` / `admin123`

### Auto-Scaling Demonstration

We demonstrate dynamic scaling behavior in response to varying load:

**Load Testing:**
```bash
cd k8s
./load-test.sh
```

**Observed Scaling Behavior:**

| Time | Load Level | CPU Usage | API Pods | Frontend Pods |
|------|------------|-----------|----------|---------------|
| 0-30s | Baseline | <30% | 3 | 2 |
| 30s-2min | Medium | 70-80% | 3→6 | 2→4 |
| 2-4min | High | 85-95% | 6→10 | 4→6 |
| 5-10min (cooldown) | None | <20% | 10→3 | 6→2 |

**Key Features:**
- Horizontal Pod Autoscaler (HPA) configured for CPU/Memory thresholds
- Automatic scale-up during traffic spikes
- Automatic scale-down to save resources
- Zero-downtime deployments with rolling updates

**Documentation**: See [`k8s/README.md`](k8s/README.md) and [`k8s/VERIFICATION_CHECKLIST.md`](k8s/VERIFICATION_CHECKLIST.md)

---

## Infrastructure as Code with Pulumi

### Overview

We use **Pulumi with Python** to automate 100% of infrastructure provisioning. All infrastructure is defined as code in [`infra/`](infra/).

### What Pulumi Automates

Our Pulumi code provisions:

1. **GKE Cluster** (6 nodes, e2-standard-2, multi-zone)
2. **Kubernetes Resources** (15+ resources):
   - Namespaces, ConfigMaps, Secrets
   - Deployments (API 3-10 replicas, Frontend 2-6 replicas)
   - StatefulSet (ChromaDB with 10Gi PVC)
   - Services (2 LoadBalancer, 1 ClusterIP)
   - Horizontal Pod Autoscalers (2 HPAs)
3. **Networking** (LoadBalancers, ClusterIP services)
4. **Storage** (Persistent Volume Claims)
5. **Configuration** (Secrets, environment variables)

### Quick Deploy

```bash
cd infra

# Install dependencies
pip install -r requirements.txt

# Deploy infrastructure
pulumi login --local
pulumi stack select dev
pulumi up

# Get deployment URLs
pulumi stack output frontend_url
pulumi stack output api_url
```

### Verification

```bash
cd infra
python verify.py
```

**Expected Output:**
```
✅ All checks passed! Your Pulumi infrastructure is complete.
Passed: 36, Failed: 0, Warnings: 1
```

### Benefits

✅ **Reproducible**: Recreate infrastructure from code  
✅ **Version Controlled**: Track changes in Git  
✅ **Automated**: One-command deployment  
✅ **Type Safe**: Python type hints catch errors early  

**Documentation**: See [`infra/README.md`](infra/README.md)

---

## Continuous Integration and Deployment

We have implemented a comprehensive CI/CD pipeline using **GitHub Actions** that automatically runs on every push and pull request to ensure code quality and system reliability.

### 1. **Build and Lint**
- **Automated Build**: Docker image is built with all dependencies and test suites
- **Code Quality Checks**: 
  - **Black**: Python code formatting validation (line length: 120 characters)
  - **Flake8**: Linting for code quality and style consistency (PEP 8 compliance)

### 2. **Run Tests**
The pipeline executes three levels of automated testing:

- **Unit Tests**: Test individual components in isolation (utils, models, services)
- **Integration Tests**: Verify interactions between API components and external services
- **System Tests (End-to-End)**: Full API testing with a running server instance

All tests run inside Docker containers to ensure consistency across environments.

### 3. **Report Coverage**
- **Code Coverage Reports**: Generated using `pytest-cov`
- **Minimum Coverage Threshold**: 50% (enforced in CI)
- **Coverage Reports**: Available as artifacts in GitHub Actions
  - Terminal output with line-by-line coverage
  - HTML reports for detailed analysis
  - XML format for integration with coverage tools

<img width="1630" height="472" alt="24101764099681_ pic_hd" src="https://github.com/user-attachments/assets/e67a80f3-f391-4ce5-b524-7eb28f72c741" />


## Test Structure

```
tests/
├── unit/              # Unit tests for individual components
│   ├── test_auth.py   # Authentication utility tests
│   ├── test_config.py # Configuration tests
│   └── test_lang.py   # Language detection tests
├── integration/       # Integration tests for API endpoints
│   └── test_api.py    # API integration tests
└── system/            # End-to-end system tests
    └── test_system_api.py  # Full system workflow tests
```




## Data Versioning and Reproducibility

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


## Model Training or Fine-Tuning

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


## Infrastructure as Code with Pulumi

We use **Pulumi** to automate the complete provisioning and deployment of our infrastructure and application. This ensures reproducible, version-controlled, and auditable infrastructure management.

### What Pulumi Automates

Our Pulumi infrastructure code (`infra/`) provisions:

1. **GKE Cluster**
   - Fully configured Kubernetes cluster on Google Cloud
   - Auto-scaling node pools with e2-standard-2 machines
   - Multi-zone deployment for high availability

2. **Networking**
   - LoadBalancer services for external access
   - Internal ClusterIP services for inter-pod communication
   - Automatic IP allocation and DNS management

3. **Storage**
   - Persistent Volume Claims (PVC) for ChromaDB
   - 10Gi storage with automatic provisioning

4. **Security & Configuration**
   - Kubernetes secrets for GCP credentials
   - ConfigMaps for environment variables
   - Namespace isolation

5. **Application Deployment**
   - API backend deployment (3-10 replicas with HPA)
   - Frontend deployment (2-6 replicas with HPA)
   - ChromaDB StatefulSet with persistent storage

6. **Auto-scaling**
   - Horizontal Pod Autoscalers (HPA) based on CPU/Memory
   - Automatic scaling between min and max replicas

### Using Pulumi

**Quick Deploy**:
```bash
cd infra

# Install dependencies
pip install -r requirements.txt

# Initialize stack
pulumi login --local  # or use Pulumi Cloud
pulumi stack select dev

# Deploy everything
pulumi up
```

**View Outputs**:
```bash
# Get all infrastructure outputs
pulumi stack output

# Get specific URLs
pulumi stack output frontend_url
pulumi stack output api_url
```

**Update Infrastructure**:
```bash
# After code changes
pulumi up

# Preview changes first
pulumi preview
```

**Destroy Infrastructure**:
```bash
pulumi destroy
```

### Benefits of IaC with Pulumi

✅ **Reproducibility**: Entire infrastructure defined in code  
✅ **Version Control**: Infrastructure changes tracked in Git  
✅ **Automation**: One command deploys everything  
✅ **State Management**: Pulumi tracks resource state automatically  
✅ **Type Safety**: Python type hints catch errors before deployment  
✅ **Multi-Cloud**: Can extend to AWS, Azure if needed  

For detailed documentation, see [`infra/README.md`](infra/README.md).


---

## Kubernetes Deployment (Production)

### ✅ Live Production System

Our application is deployed on **Google Kubernetes Engine (GKE)** and is **accessible 24/7**:

- **Frontend Application**: http://34.136.237.225
- **API Documentation**: http://136.111.94.120:9000/api/docs
- **Health Check**: http://136.111.94.120:9000/api/v1/health

**Default Credentials:**
```
Username: admin
Password: admin123
```

### Deployment Architecture

**Cluster Configuration:**
- **Platform**: Google Kubernetes Engine (GKE)
- **Region**: us-central1
- **Cluster Name**: safety-event-cluster
- **Nodes**: 6 nodes (e2-standard-2, 2 CPUs each)
- **Namespace**: safety-event-system

**Deployed Services:**

1. **API Backend Service** ✅
   - **Access URL**: http://136.111.94.120:9000
   - **API Documentation**: http://136.111.94.120:9000/api/docs
   - **Deployment**: 3 replicas with auto-scaling (3-10 pods)
   - **Service Type**: LoadBalancer
   - **Health Check**: http://136.111.94.120:9000/api/v1/health

2. **Frontend Service** ✅
   - **Access URL**: http://34.136.237.225
   - **Deployment**: 2 replicas with auto-scaling (2-6 pods)
   - **Service Type**: LoadBalancer
   - **Framework**: Next.js 15

3. **ChromaDB (Vector Database)**
   - **Type**: StatefulSet with persistent storage (10Gi)
   - **Service Type**: ClusterIP (internal only)
   - **Port**: 8000

### Key Features

**1. Auto-Scaling (HPA - Horizontal Pod Autoscaler)**
- API: Scales from 3 to 10 pods based on CPU (70%) and Memory (80%) usage
- Frontend: Scales from 2 to 6 pods based on load
- Automatically handles traffic spikes and reduces costs during low usage

**2. High Availability**
- Multiple replicas ensure zero downtime
- Automatic pod restart on failure
- Load balancing across all replicas

**3. Production-Ready Configuration**
- Resource limits and requests defined
- Liveness and readiness probes configured
- Persistent storage for database
- Environment-specific configurations via ConfigMaps

### Accessing the Production Deployment

**Live URLs (24/7 available):**
- **Frontend Application**: http://34.136.237.225
- **API Documentation**: http://136.111.94.120:9000/api/docs
- **Health Check**: http://136.111.94.120:9000/api/v1/health

**Default Credentials:**
```
Username: admin
Password: admin123
```

### Deployment Files

All Kubernetes configuration files are located in the `k8s/` directory:

```
k8s/
├── deploy.sh                    # Automated deployment script
├── namespace.yaml               # Namespace configuration
├── configmap.yaml              # Environment variables
├── secret.yaml                 # GCP credentials
├── api-deployment.yaml         # API backend deployment
├── frontend-deployment.yaml    # Frontend deployment
├── chromadb-statefulset.yaml   # Vector database
├── hpa.yaml                    # Auto-scaling configuration
├── load-test.sh                # Load testing script
├── VERIFICATION_CHECKLIST.md   # Deployment verification guide
└── README.md                   # Kubernetes documentation
```

### Deploying to Kubernetes

**Prerequisites:**
```bash
# Install gcloud CLI and kubectl
gcloud components install kubectl gke-gcloud-auth-plugin

# Configure GCP project
gcloud config set project apcomp215-group88
gcloud config set compute/region us-central1
```

**One-Command Deployment:**
```bash
cd k8s
chmod +x deploy.sh
./deploy.sh
```

This script will:
1. Create GKE cluster (if not exists)
2. Configure kubectl access
3. Create namespace and secrets
4. Deploy all services
5. Set up auto-scaling
6. Display access URLs

**Manual Deployment Steps:**

1. **Build and Push Docker Images:**
```bash
# Build for amd64 platform
cd src/api
docker buildx build --platform linux/amd64 \
  -t gcr.io/apcomp215-group88/safety-event-api:latest --push .

cd ../frontend-react
docker buildx build --platform linux/amd64 \
  -t gcr.io/apcomp215-group88/safety-event-frontend:latest --push .
```

2. **Deploy to Kubernetes:**
```bash
# Get cluster credentials
gcloud container clusters get-credentials safety-event-cluster \
  --region=us-central1

# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic gcp-credentials \
  --from-file=key.json=secrets/llm-service-account.json \
  -n safety-event-system

# Deploy services
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/chromadb-statefulset.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/hpa.yaml
```

3. **Verify Deployment:**
```bash
# Check all resources
kubectl get all -n safety-event-system

# Check pod status
kubectl get pods -n safety-event-system

# Get external IPs
kubectl get services -n safety-event-system

# View logs
kubectl logs -l app=safety-event-api -n safety-event-system
```

### Monitoring and Management

**View Deployment Status:**
```bash
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

# View all resources
kubectl get all -n safety-event-system

# Check auto-scaling status
kubectl get hpa -n safety-event-system

# View pod details
kubectl describe pods -n safety-event-system
```

**Access Pod Shell:**
```bash
# API backend
kubectl exec -it deployment/api-deployment -n safety-event-system -- /bin/bash

# Frontend
kubectl exec -it deployment/frontend-deployment -n safety-event-system -- /bin/bash
```

**View Logs:**
```bash
# API logs
kubectl logs -f deployment/api-deployment -n safety-event-system

# Frontend logs
kubectl logs -f deployment/frontend-deployment -n safety-event-system
```

**Update Deployment:**
```bash
# After code changes, rebuild and push image
docker buildx build --platform linux/amd64 \
  -t gcr.io/apcomp215-group88/safety-event-api:latest --push .

# Restart pods to pull new image
kubectl rollout restart deployment/api-deployment -n safety-event-system
```

### Load Testing and Auto-Scaling Demonstration

Test the auto-scaling capabilities:

```bash
cd k8s
chmod +x load-test.sh
./load-test.sh
```

This will:
1. Generate baseline load
2. Gradually increase to 50 concurrent users
3. Spike to 100 users
4. Sustain heavy load
5. Monitor pod scaling in real-time

**Expected Behavior:**
- Start: 3 API pods, 2 Frontend pods
- Under load: Scales up to 8-10 API pods, 4-6 Frontend pods
- After load: Automatically scales back down

### Cost Management

**Current Estimated Costs:**
- 6 nodes × e2-standard-2: ~$150/month
- LoadBalancer IPs: ~$20/month
- Persistent storage: ~$2/month
- **Total**: ~$172/month

**To Stop Services (Save Costs):**
```bash
# Delete namespace only (keep cluster)
kubectl delete namespace safety-event-system

# Or delete entire cluster
gcloud container clusters delete safety-event-cluster --region=us-central1
```

### Advantages of Kubernetes Deployment

1. **Production Ready**: 24/7 availability from anywhere
2. **Auto-Scaling**: Handles traffic spikes automatically
3. **High Availability**: Multiple replicas with automatic failover
4. **Resource Efficiency**: Scales down during low usage
5. **Professional Infrastructure**: Industry-standard deployment
6. **Easy Updates**: Rolling updates with zero downtime
7. **Monitoring**: Built-in health checks and logging

## Frontend UI Preview

<img width="1504" height="843" alt="Screenshot 2025-11-25 at 15 04 01" src="https://github.com/user-attachments/assets/277a1ddf-ce4c-4597-b1ec-3865fedf418f" />

<img width="1506" height="823" alt="Screenshot 2025-11-25 at 15 04 24" src="https://github.com/user-attachments/assets/9489950c-10d5-4bda-a827-cd883f5f4427" />

<img width="1484" height="855" alt="Screenshot 2025-11-25 at 15 04 51" src="https://github.com/user-attachments/assets/0b799647-953e-4cd0-8eac-73e11a04e1a9" />

<img width="1506" height="851" alt="Screenshot 2025-11-25 at 15 05 11" src="https://github.com/user-attachments/assets/0842f3d6-a4af-4879-9eeb-a3b9bee665e0" />

<img width="1500" height="844" alt="Screenshot 2025-11-25 at 15 05 22" src="https://github.com/user-attachments/assets/792c13d2-d406-49d6-9b48-131bee139b5e" />

<img width="1510" height="848" alt="Screenshot 2025-11-25 at 15 05 34" src="https://github.com/user-attachments/assets/fef2cb74-cf86-4c1a-9e36-1e18a5feaaeb" />

<img width="1510" height="848" alt="Screenshot 2025-11-25 at 15 05 54" src="https://github.com/user-attachments/assets/88e9b2c5-d10b-46e0-9156-6df613e4117f" />

---

## Known Issues and Limitations

### Test Coverage Limitations

**Current Coverage**: 65% (exceeds 60% requirement)

**Modules Not Fully Covered:**

1. **Audio Transcription (55%)**
   - **Reason**: Complex integration with Google Whisper API
   - **Challenge**: Mocking audio file uploads and streaming responses
   - **Plan**: Add audio fixtures and mock Whisper responses

2. **RAG Retrieval (48%)**
   - **Reason**: ChromaDB requires live vector database connection
   - **Challenge**: Mocking embeddings and similarity search
   - **Plan**: Implement ChromaDB test fixtures with pre-computed embeddings

3. **Batch Processing (52%)**
   - **Reason**: File upload edge cases (large files, malformed CSVs)
   - **Challenge**: Testing multipart/form-data with FastAPI
   - **Plan**: Add comprehensive file upload test suite

4. **Admin Endpoints (25%)**
   - **Reason**: Requires authenticated session setup in tests
   - **Challenge**: Session management and JWT token mocking
   - **Plan**: Implement test authentication middleware

5. **WebSocket Handlers (15%)**
   - **Reason**: Real-time features not prioritized for MVP
   - **Challenge**: Testing asynchronous WebSocket connections
   - **Plan**: Add WebSocket test clients if feature becomes critical

### Known Issues

1. **Initial Load Time**
   - **Issue**: First API call after deployment may take 10-15 seconds
   - **Cause**: Cold start of Vertex AI model
   - **Workaround**: Health check endpoint keeps API warm
   - **Status**: Acceptable for current usage

2. **ChromaDB Persistence**
   - **Issue**: Vector database data lost if StatefulSet is deleted
   - **Cause**: PVC is tied to StatefulSet lifecycle
   - **Workaround**: Use backup/restore scripts in `src/vector-db/`
   - **Plan**: Implement automated backups to GCS

3. **Frontend Session Timeout**
   - **Issue**: Users logged out after 1 hour of inactivity
   - **Cause**: JWT token expiration
   - **Workaround**: Re-login required
   - **Plan**: Implement token refresh mechanism

4. **Audio File Size Limit**
   - **Issue**: Audio uploads limited to 10MB
   - **Cause**: FastAPI default multipart limits
   - **Workaround**: Split large audio files
   - **Plan**: Increase limit or implement chunked upload

5. **Language Detection Accuracy**
   - **Issue**: Mixed-language incidents may misdetect primary language
   - **Cause**: Language detection relies on first 200 characters
   - **Workaround**: Manual language selection available
   - **Status**: Acceptable accuracy (>95%) for single-language text

### Performance Limitations

| Component | Current | Target | Notes |
|-----------|---------|--------|-------|
| API Response Time | 3-5s | <3s | Depends on Vertex AI latency |
| Classification Accuracy | ~85% | >90% | Based on manual validation |
| Concurrent Users | ~50 | 100+ | Limited by GKE node capacity |
| Audio Transcription | 30s/min | 15s/min | Whisper API limitation |

### Future Improvements

**Short-term (Next Sprint):**
- [ ] Increase test coverage to 80%
- [ ] Implement token refresh for frontend
- [ ] Add automated ChromaDB backups
- [ ] Optimize API response caching

**Medium-term (Next Milestone):**
- [ ] Fine-tune model for hospital-specific terminology
- [ ] Implement user role management (beyond admin/user)
- [ ] Add audit logging for compliance
- [ ] Multi-tenancy support for multiple hospitals

**Long-term (Production):**
- [ ] HIPAA compliance certification
- [ ] Integration with EHR systems (Epic, Cerner)
- [ ] Advanced analytics dashboard
- [ ] Mobile app (iOS/Android)

### Support and Documentation

**Primary Documentation:**
- API: [`src/api/README.md`](src/api/README.md)
- Frontend: [`src/frontend-react/README.md`](src/frontend-react/README.md)
- Kubernetes: [`k8s/README.md`](k8s/README.md)
- Pulumi IaC: [`infra/README.md`](infra/README.md)
- RAG/Vector DB: [`src/vector-db/README.md`](src/vector-db/README.md)

**Contact:**
- GitHub Issues: https://github.com/JingxiZhang-77/AC215_888/issues
- Team Email: [Contact through GitHub]

---

## License

This project is developed for academic purposes as part of Harvard AC215: MLOps.

