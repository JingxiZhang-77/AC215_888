#!/bin/bash

# Load Testing Script for Kubernetes Deployment
# Demonstrates auto-scaling behavior under varying load

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="safety-event-system"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Load Testing & Scaling Demonstration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get API service external IP
echo -e "${GREEN}Getting API service endpoint...${NC}"
API_IP=$(kubectl get service api-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$API_IP" ]; then
    echo -e "${RED}Error: Could not get API external IP${NC}"
    echo "Make sure the service is deployed and LoadBalancer has been provisioned"
    exit 1
fi

API_URL="http://${API_IP}:9000"
echo -e "${GREEN}API URL: ${API_URL}${NC}"
echo ""

# Check initial status
echo -e "${BLUE}Initial Deployment Status:${NC}"
kubectl get deployments -n ${NAMESPACE}
echo ""
kubectl get pods -n ${NAMESPACE}
echo ""
kubectl get hpa -n ${NAMESPACE}
echo ""

# Function to run load test
run_load_test() {
    local duration=$1
    local concurrent=$2
    local requests=$3
    local phase=$4

    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}${phase}${NC}"
    echo -e "${YELLOW}Duration: ${duration}s | Concurrent: ${concurrent} | Total Requests: ${requests}${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    # Start load test in background
    echo -e "${GREEN}Starting load test...${NC}"
    
    # Using Apache Bench (ab)
    ab -n ${requests} -c ${concurrent} -t ${duration} ${API_URL}/api/v1/health > /tmp/ab-results.txt 2>&1 &
    LOAD_PID=$!
    
    # Monitor for specified duration
    echo -e "${GREEN}Monitoring for ${duration} seconds...${NC}"
    for i in $(seq 1 ${duration}); do
        if [ $((i % 10)) -eq 0 ]; then
            echo ""
            echo -e "${BLUE}--- Status at ${i}s ---${NC}"
            kubectl get hpa api-hpa -n ${NAMESPACE}
            echo ""
            kubectl get pods -l app=safety-event-api -n ${NAMESPACE} --no-headers | wc -l | xargs echo "API Pods:"
        fi
        sleep 1
    done
    
    # Wait for load test to complete
    wait $LOAD_PID 2>/dev/null
    
    echo ""
    echo -e "${GREEN}Load test results:${NC}"
    grep -E "Requests per second|Time per request|Transfer rate" /tmp/ab-results.txt || true
    echo ""
}

# Phase 1: Baseline (low load)
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 1: Baseline - Low Load${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Initial pod count (should be at minimum replicas: 3)${NC}"
kubectl get pods -l app=safety-event-api -n ${NAMESPACE}
echo ""
sleep 5

# Phase 2: Medium load
run_load_test 60 20 10000 "Phase 2: Medium Load - Triggering Scale Up"

echo ""
echo -e "${GREEN}Waiting 30s for HPA to react...${NC}"
sleep 30

echo ""
echo -e "${BLUE}HPA Status after medium load:${NC}"
kubectl get hpa -n ${NAMESPACE}
echo ""
kubectl get pods -l app=safety-event-api -n ${NAMESPACE}
echo ""

# Phase 3: High load
run_load_test 90 50 50000 "Phase 3: High Load - Maximum Scale Up"

echo ""
echo -e "${GREEN}Waiting 30s for HPA to react...${NC}"
sleep 30

echo ""
echo -e "${BLUE}HPA Status after high load:${NC}"
kubectl get hpa -n ${NAMESPACE}
echo ""
kubectl get pods -l app=safety-event-api -n ${NAMESPACE}
echo ""

# Phase 4: Cool down (scale down)
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 4: Cool Down - Scale Down${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Waiting for scale down (this may take 5-10 minutes due to stabilization window)${NC}"

for i in $(seq 1 10); do
    echo ""
    echo -e "${BLUE}--- Cool down check $i/10 (${i} min) ---${NC}"
    kubectl get hpa -n ${NAMESPACE}
    echo ""
    kubectl get pods -l app=safety-event-api -n ${NAMESPACE} --no-headers | wc -l | xargs echo "Current API Pods:"
    sleep 60
done

# Final summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Load Test Complete - Final Status${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${BLUE}Deployments:${NC}"
kubectl get deployments -n ${NAMESPACE}
echo ""

echo -e "${BLUE}HPA Status:${NC}"
kubectl get hpa -n ${NAMESPACE}
echo ""

echo -e "${BLUE}Pods:${NC}"
kubectl get pods -n ${NAMESPACE}
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Scaling Behavior Summary:${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "1. Started with minimum 3 replicas (baseline)"
echo "2. Scaled up during medium load (20 concurrent requests)"
echo "3. Scaled to maximum capacity during high load (50 concurrent requests)"
echo "4. Automatically scaled down after load decreased"
echo ""
echo -e "${BLUE}To view detailed HPA events:${NC}"
echo "kubectl describe hpa api-hpa -n ${NAMESPACE}"
echo ""
echo -e "${BLUE}To view pod events:${NC}"
echo "kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp'"
echo ""
