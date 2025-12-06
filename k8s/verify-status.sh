#!/bin/bash

export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

echo "========================================="
echo "Kubernetes Deployment Verification Report"
echo "========================================="
echo ""

echo "1. Cluster Node Status:"
kubectl get nodes --no-headers | wc -l | xargs echo "Node Count:"
echo ""

echo "2. Pod Status:"
kubectl get pods -n safety-event-system --no-headers 2>/dev/null | awk '{print $1 " - " $3}' || echo "Unable to retrieve Pod status"
echo ""

echo "3. Service External IPs:"
kubectl get services -n safety-event-system --no-headers 2>/dev/null | awk '{print $1 ": " $4}' || echo "Unable to retrieve Service status"
echo ""

echo "4. HPA Status:"
kubectl get hpa -n safety-event-system --no-headers 2>/dev/null | awk '{print $1 " - Replicas: " $5}' || echo "Unable to retrieve HPA status"
echo ""

API_IP="136.111.94.120"
FRONTEND_IP="34.136.237.225"

echo "5. API Access Test:"
echo "API URL: http://${API_IP}:9000"
timeout 3 curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://${API_IP}:9000/api/v1/health 2>/dev/null || echo "API not responding"
echo ""

echo "6. Frontend Access Test:"
echo "Frontend URL: http://${FRONTEND_IP}"
timeout 3 curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://${FRONTEND_IP} 2>/dev/null || echo "Frontend not responding"
echo ""

echo "========================================="
echo "Verification Complete"
echo "========================================="
