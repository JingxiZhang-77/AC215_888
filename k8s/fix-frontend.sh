#!/bin/bash

# Frontend Fix Script
# Attempts to fix common frontend deployment issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="apcomp215-group88"
NAMESPACE="safety-event-system"
CLUSTER_NAME="safety-event-cluster"
REGION="us-central1"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Frontend Fix Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Connect to cluster
echo -e "${GREEN}Step 1: Connecting to GKE cluster...${NC}"
gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${REGION}

# Rebuild and push frontend image
echo -e "${GREEN}Step 2: Rebuilding frontend image for AMD64 platform...${NC}"
cd src/frontend-react
docker buildx build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/safety-event-frontend:latest -f Dockerfile . --push
cd ../..

# Delete existing pods to force new image pull
echo -e "${GREEN}Step 3: Restarting frontend pods...${NC}"
kubectl rollout restart deployment/frontend-deployment -n ${NAMESPACE}

# Wait for rollout
echo -e "${YELLOW}Waiting for deployment rollout...${NC}"
kubectl rollout status deployment/frontend-deployment -n ${NAMESPACE} --timeout=300s

# Check pod status
echo -e "${GREEN}Step 4: Checking pod status...${NC}"
kubectl get pods -n ${NAMESPACE} -l app=safety-event-frontend

# Get service IP
echo -e "${GREEN}Step 5: Getting LoadBalancer IP...${NC}"
FRONTEND_IP=$(kubectl get service frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo -e "${BLUE}Frontend IP: ${FRONTEND_IP}${NC}"

# Test accessibility
echo -e "${GREEN}Step 6: Testing frontend accessibility...${NC}"
sleep 10
if curl -f -s -o /dev/null http://${FRONTEND_IP}; then
    echo -e "${GREEN}✅ Frontend is accessible at http://${FRONTEND_IP}${NC}"
else
    echo -e "${RED}❌ Frontend is not accessible yet${NC}"
    echo -e "${YELLOW}Checking logs...${NC}"
    kubectl logs -n ${NAMESPACE} -l app=safety-event-frontend --tail=20
fi

echo -e "${GREEN}Fix attempt complete!${NC}"
