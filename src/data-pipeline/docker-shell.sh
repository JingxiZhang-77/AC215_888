#!/bin/bash

# Data Pipeline - Docker Shell Script
# Builds and runs the data generation container with proper environment configuration

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Configuration
export IMAGE_NAME="data-pipeline"
export BASE_DIR="$SCRIPT_DIR"
export SECRETS_DIR="$(cd "$SCRIPT_DIR/../../secrets" && pwd)"
export GCP_PROJECT="apcomp215-group88"
export GCP_REGION="us-central1"

echo "============================================"
echo "Data Pipeline - Docker Setup"
echo "============================================"
echo "Build directory: $BASE_DIR"

# Check if secrets directory exists
if [ ! -d "$SECRETS_DIR" ]; then
    echo "Error: Secrets directory not found at $SECRETS_DIR"
    echo "Please ensure llm-service-account.json is available"
    exit 1
fi

# Build the image
echo "Building Docker image: $IMAGE_NAME"
cd "$BASE_DIR"
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container
echo "Starting data pipeline container..."
docker run --rm --name $IMAGE_NAME -ti \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e GCP_REGION=$GCP_REGION \
    $IMAGE_NAME
