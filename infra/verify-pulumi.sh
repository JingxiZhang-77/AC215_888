#!/bin/bash

echo "================================================"
echo "Pulumi Infrastructure Verification Checklist"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

echo "1. File Structure"
echo "─────────────────"

# Check required files
if [ -f "__main__.py" ]; then
    check_pass "__main__.py exists"
else
    check_fail "__main__.py missing"
fi

if [ -f "Pulumi.yaml" ]; then
    check_pass "Pulumi.yaml exists"
else
    check_fail "Pulumi.yaml missing"
fi

if [ -f "Pulumi.dev.yaml" ]; then
    check_pass "Pulumi.dev.yaml exists"
else
    check_fail "Pulumi.dev.yaml missing"
fi

if [ -f "Pulumi.prod.yaml" ]; then
    check_pass "Pulumi.prod.yaml exists"
else
    check_fail "Pulumi.prod.yaml missing"
fi

if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt exists"
else
    check_fail "requirements.txt missing"
fi

if [ -f "README.md" ]; then
    check_pass "README.md exists"
else
    check_fail "README.md missing"
fi

if [ -f ".gitignore" ]; then
    check_pass ".gitignore exists"
else
    check_fail ".gitignore missing"
fi

echo ""
echo "2. Python Syntax Check"
echo "──────────────────────"

if python3 -m py_compile __main__.py 2>&1; then
    check_pass "Python syntax is valid"
else
    check_fail "Python syntax errors found"
fi

echo ""
echo "3. Code Structure Analysis"
echo "──────────────────────────"

# Check for key components in __main__.py
if grep -q "pulumi_gcp" __main__.py; then
    check_pass "GCP provider imported"
else
    check_fail "GCP provider not found"
fi

if grep -q "pulumi_kubernetes" __main__.py; then
    check_pass "Kubernetes provider imported"
else
    check_fail "Kubernetes provider not found"
fi

if grep -q "gcp.container.Cluster" __main__.py; then
    check_pass "GKE cluster definition found"
else
    check_fail "GKE cluster definition missing"
fi

if grep -q "Namespace" __main__.py; then
    check_pass "Kubernetes namespace definition found"
else
    check_fail "Namespace definition missing"
fi

if grep -q "Secret" __main__.py; then
    check_pass "Secret management found"
else
    check_fail "Secret management missing"
fi

if grep -q "Deployment.*api-deployment" __main__.py; then
    check_pass "API deployment found"
else
    check_fail "API deployment missing"
fi

if grep -q "Deployment.*frontend-deployment" __main__.py; then
    check_pass "Frontend deployment found"
else
    check_fail "Frontend deployment missing"
fi

if grep -q "StatefulSet.*chromadb" __main__.py; then
    check_pass "ChromaDB StatefulSet found"
else
    check_fail "ChromaDB StatefulSet missing"
fi

if grep -q "Service.*LoadBalancer" __main__.py; then
    check_pass "LoadBalancer services found"
else
    check_fail "LoadBalancer services missing"
fi

if grep -q "HorizontalPodAutoscaler" __main__.py; then
    check_pass "Auto-scaling (HPA) found"
else
    check_fail "Auto-scaling (HPA) missing"
fi

if grep -q "PersistentVolumeClaim" __main__.py; then
    check_pass "Persistent storage found"
else
    check_fail "Persistent storage missing"
fi

if grep -q "pulumi.export" __main__.py; then
    check_pass "Output exports found"
else
    check_fail "Output exports missing"
fi

echo ""
echo "4. Configuration Check"
echo "──────────────────────"

# Check Pulumi.yaml
if grep -q "runtime: python" Pulumi.yaml; then
    check_pass "Python runtime specified"
else
    check_fail "Python runtime not specified"
fi

if grep -q "name: safety-event-system-infra" Pulumi.yaml; then
    check_pass "Project name configured"
else
    check_fail "Project name not configured"
fi

# Check stack configs
if grep -q "gcp:project" Pulumi.dev.yaml; then
    check_pass "GCP project configured in dev stack"
else
    check_fail "GCP project not configured in dev stack"
fi

if grep -q "gcp:region" Pulumi.dev.yaml; then
    check_pass "GCP region configured"
else
    check_fail "GCP region not configured"
fi

if grep -q "gcpServiceAccountPath" Pulumi.dev.yaml; then
    check_pass "Service account path configured"
else
    check_fail "Service account path not configured"
fi

echo ""
echo "5. Dependencies Check"
echo "─────────────────────"

if grep -q "pulumi>=" requirements.txt; then
    check_pass "Pulumi package specified"
else
    check_fail "Pulumi package missing"
fi

if grep -q "pulumi-gcp>=" requirements.txt; then
    check_pass "Pulumi GCP provider specified"
else
    check_fail "Pulumi GCP provider missing"
fi

if grep -q "pulumi-kubernetes>=" requirements.txt; then
    check_pass "Pulumi Kubernetes provider specified"
else
    check_fail "Pulumi Kubernetes provider missing"
fi

echo ""
echo "6. Prerequisites Check"
echo "──────────────────────"

if command -v pulumi &> /dev/null; then
    check_pass "Pulumi CLI installed ($(pulumi version))"
else
    check_warn "Pulumi CLI not installed (optional for verification)"
fi

if command -v gcloud &> /dev/null; then
    check_pass "gcloud CLI installed"
else
    check_warn "gcloud CLI not installed (needed for deployment)"
fi

if [ -f "../secrets/llm-service-account.json" ]; then
    check_pass "GCP service account key exists"
else
    check_warn "GCP service account key not found at ../secrets/llm-service-account.json"
fi

if command -v python3 &> /dev/null; then
    check_pass "Python 3 installed ($(python3 --version))"
else
    check_fail "Python 3 not installed"
fi

echo ""
echo "7. Infrastructure Components Checklist"
echo "───────────────────────────────────────"

echo "Components defined in __main__.py:"
echo ""

# Count resources
CLUSTERS=$(grep -c "gcp.container.Cluster" __main__.py || echo "0")
NAMESPACES=$(grep -c "Namespace(" __main__.py || echo "0")
SECRETS=$(grep -c "Secret(" __main__.py || echo "0")
CONFIGMAPS=$(grep -c "ConfigMap(" __main__.py || echo "0")
DEPLOYMENTS=$(grep -c "Deployment(" __main__.py || echo "0")
SERVICES=$(grep -c "Service(" __main__.py || echo "0")
STATEFULSETS=$(grep -c "StatefulSet(" __main__.py || echo "0")
HPAS=$(grep -c "HorizontalPodAutoscaler(" __main__.py || echo "0")
PVCS=$(grep -c "PersistentVolumeClaim(" __main__.py || echo "0")

echo "  • GKE Clusters: $CLUSTERS"
echo "  • Namespaces: $NAMESPACES"
echo "  • Secrets: $SECRETS"
echo "  • ConfigMaps: $CONFIGMAPS"
echo "  • Deployments: $DEPLOYMENTS"
echo "  • Services: $SERVICES"
echo "  • StatefulSets: $STATEFULSETS"
echo "  • HPAs: $HPAS"
echo "  • PVCs: $PVCS"

if [ $CLUSTERS -ge 1 ] && [ $DEPLOYMENTS -ge 2 ] && [ $SERVICES -ge 3 ] && [ $HPAS -ge 2 ]; then
    check_pass "All critical infrastructure components present"
else
    check_fail "Some critical infrastructure components missing"
fi

echo ""
echo "8. Documentation Check"
echo "──────────────────────"

if grep -q "## Overview" README.md; then
    check_pass "README has Overview section"
else
    check_warn "README missing Overview section"
fi

if grep -q "## Prerequisites" README.md; then
    check_pass "README has Prerequisites section"
else
    check_warn "README missing Prerequisites section"
fi

if grep -q "pulumi up" README.md; then
    check_pass "README has deployment instructions"
else
    check_warn "README missing deployment instructions"
fi

echo ""
echo "================================================"
echo "Summary"
echo "================================================"
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${RED}Failed:${NC} $FAIL"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Your Pulumi infrastructure code is complete and ready."
    echo ""
    echo "Next steps:"
    echo "1. Install Pulumi: curl -fsSL https://get.pulumi.com | sh"
    echo "2. Install dependencies: pip install -r requirements.txt"
    echo "3. Deploy: pulumi up"
    exit 0
else
    echo -e "${RED}✗ Some checks failed!${NC}"
    echo "Please fix the issues above before deploying."
    exit 1
fi
