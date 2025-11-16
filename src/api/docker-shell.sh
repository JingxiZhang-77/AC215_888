#!/bin/bash

# Safety Event Classification API - Docker Shell Script
# Builds and runs the API container with proper environment configuration

# Exit on error
set -e

# Configuration
export IMAGE_NAME="safety-event-api"
export REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
export API_DIR="$REPO_ROOT/src/api"
export SECRETS_DIR="$REPO_ROOT/secrets"
export GCP_PROJECT="apcomp215-group88"
export GCP_REGION="us-central1"

# Check if secrets directory exists
if [ ! -d "$SECRETS_DIR" ]; then
    echo "Error: Secrets directory not found at $SECRETS_DIR"
    echo "Please ensure llm-service-account.json is available"
    exit 1
fi

# Build the image
echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME -f "$API_DIR/Dockerfile" "$REPO_ROOT"

# Run the container
echo "Starting API container..."
docker run --rm --name $IMAGE_NAME -ti \
    -v "$REPO_ROOT":/app \
    -v "$SECRETS_DIR":/secrets \
    -p 9000:9000 \
    -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e GCP_REGION=$GCP_REGION \
    -e ENVIRONMENT=development \
    -e DEBUG=true \
    -e PORT=9000 \
    $IMAGE_NAME
