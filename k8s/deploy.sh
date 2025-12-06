#!/bin/bash

# Kubernetes Deployment Script for Safety Event Classification System
# Deploys application to GKE cluster with auto-scaling enabled

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Kubernetes Deployment Script${NC}"
echo -e "${BLUE}Safety Event Classification System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Configuration
PROJECT_ID="apcomp215-group88"
REGION="us-central1"
CLUSTER_NAME="safety-event-cluster"
NAMESPACE="safety-event-system"

# Step 1: Set up GCP project
echo -e "${GREEN}Step 1: Setting up GCP project...${NC}"
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}

# Step 2: Create GKE cluster (if it doesn't exist)
echo -e "${GREEN}Step 2: Checking GKE cluster...${NC}"
if gcloud container clusters describe ${CLUSTER_NAME} --region=${REGION} &>/dev/null; then
    echo -e "${YELLOW}Cluster ${CLUSTER_NAME} already exists${NC}"
else
    echo -e "${GREEN}Creating GKE cluster ${CLUSTER_NAME}...${NC}"
    gcloud container clusters create ${CLUSTER_NAME} \
        --region=${REGION} \
        --num-nodes=2 \
        --machine-type=e2-standard-2 \
        --enable-autoscaling \
        --min-nodes=2 \
        --max-nodes=6 \
        --enable-autorepair \
        --enable-autoupgrade \
        --disk-size=30GB \
        --disk-type=pd-standard
fi

# Step 3: Get cluster credentials
echo -e "${GREEN}Step 3: Getting cluster credentials...${NC}"
gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${REGION}

# Step 4: Build and push Docker images
echo -e "${GREEN}Step 4: Building and pushing Docker images...${NC}"

echo -e "${YELLOW}Building API image...${NC}"
cd src/api
docker build -t gcr.io/${PROJECT_ID}/safety-event-api:latest -f Dockerfile .
docker push gcr.io/${PROJECT_ID}/safety-event-api:latest

echo -e "${YELLOW}Building Frontend image...${NC}"
cd ../frontend-react
docker build -t gcr.io/${PROJECT_ID}/safety-event-frontend:latest -f Dockerfile .
docker push gcr.io/${PROJECT_ID}/safety-event-frontend:latest

cd ../..

# Step 5: Create namespace
echo -e "${GREEN}Step 5: Creating Kubernetes namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

# Step 6: Create secrets
echo -e "${GREEN}Step 6: Creating secrets...${NC}"
kubectl create secret generic gcp-credentials \
    --from-file=llm-service-account.json=./secrets/llm-service-account.json \
    -n ${NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 7: Apply ConfigMap
echo -e "${GREEN}Step 7: Applying ConfigMap...${NC}"
kubectl apply -f k8s/configmap.yaml

# Step 8: Deploy ChromaDB
echo -e "${GREEN}Step 8: Deploying ChromaDB...${NC}"
kubectl apply -f k8s/chromadb-statefulset.yaml

# Wait for ChromaDB to be ready
echo -e "${YELLOW}Waiting for ChromaDB to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=chromadb -n ${NAMESPACE} --timeout=300s

# Step 9: Deploy API
echo -e "${GREEN}Step 9: Deploying API...${NC}"
kubectl apply -f k8s/api-deployment.yaml

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
kubectl wait --for=condition=available deployment/api-deployment -n ${NAMESPACE} --timeout=300s

# Step 10: Deploy Frontend
echo -e "${GREEN}Step 10: Deploying Frontend...${NC}"
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for Frontend to be ready
echo -e "${YELLOW}Waiting for Frontend to be ready...${NC}"
kubectl wait --for=condition=available deployment/frontend-deployment -n ${NAMESPACE} --timeout=300s

# Step 11: Apply HPA
echo -e "${GREEN}Step 11: Applying Horizontal Pod Autoscalers...${NC}"
kubectl apply -f k8s/hpa.yaml

# Step 12: Display deployment status
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${BLUE}Deployment Status:${NC}"
kubectl get deployments -n ${NAMESPACE}

echo ""
echo -e "${BLUE}Pods Status:${NC}"
kubectl get pods -n ${NAMESPACE}

echo ""
echo -e "${BLUE}Services:${NC}"
kubectl get services -n ${NAMESPACE}

echo ""
echo -e "${BLUE}HPA Status:${NC}"
kubectl get hpa -n ${NAMESPACE}

echo ""
echo -e "${GREEN}Get external IPs:${NC}"
echo "API: kubectl get service api-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
echo "Frontend: kubectl get service frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"

echo ""
echo -e "${GREEN}To monitor scaling:${NC}"
echo "kubectl get hpa -n ${NAMESPACE} --watch"
echo ""
echo -e "${GREEN}To see logs:${NC}"
echo "kubectl logs -f deployment/api-deployment -n ${NAMESPACE}"
echo ""
