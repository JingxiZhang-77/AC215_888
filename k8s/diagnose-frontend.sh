#!/bin/bash

# Frontend Diagnostic Script
# Diagnoses issues with the frontend deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="safety-event-system"
CLUSTER_NAME="safety-event-cluster"
REGION="us-central1"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Frontend Diagnostic Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Connect to cluster
echo -e "${GREEN}Connecting to GKE cluster...${NC}"
gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${REGION}

# Check frontend deployment
echo -e "${YELLOW}Checking frontend deployment...${NC}"
kubectl get deployment frontend-deployment -n ${NAMESPACE}
echo ""

# Check frontend pods
echo -e "${YELLOW}Checking frontend pods...${NC}"
kubectl get pods -n ${NAMESPACE} -l app=safety-event-frontend
echo ""

# Check pod details
echo -e "${YELLOW}Describing frontend pods...${NC}"
kubectl describe pods -n ${NAMESPACE} -l app=safety-event-frontend
echo ""

# Check frontend service
echo -e "${YELLOW}Checking frontend service...${NC}"
kubectl get service frontend-service -n ${NAMESPACE}
kubectl describe service frontend-service -n ${NAMESPACE}
echo ""

# Get LoadBalancer IP
echo -e "${YELLOW}LoadBalancer external IP:${NC}"
kubectl get service frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
echo -e "\n"

# Check recent logs
echo -e "${YELLOW}Recent frontend logs:${NC}"
kubectl logs -n ${NAMESPACE} -l app=safety-event-frontend --tail=50
echo ""

# Check events
echo -e "${YELLOW}Recent events:${NC}"
kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp' | grep frontend
echo ""

# Test health from inside cluster
echo -e "${YELLOW}Testing frontend health from inside cluster...${NC}"
kubectl run -it --rm debug --image=alpine --restart=Never -n ${NAMESPACE} -- sh -c "apk add curl && curl -I http://frontend-service:80" || true
echo ""

echo -e "${GREEN}Diagnostic complete!${NC}"
