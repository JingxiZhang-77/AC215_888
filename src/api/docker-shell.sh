#!/bin/bash

# Safety Event Classification API - Docker Shell Script
# Builds and runs the API container with proper environment configuration

# Exit on error
set -e

# Configuration
export IMAGE_NAME="safety-event-api"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export GCP_PROJECT="apcomp215-group88"
export GCP_REGION="us-central1"
export CHROMADB_HOST="safety-chromadb"
export CHROMADB_PORT="8000"

# Check if secrets directory exists
if [ ! -d "$SECRETS_DIR" ]; then
    echo "Error: Secrets directory not found at $SECRETS_DIR"
    echo "Please ensure llm-service-account.json is available"
    exit 1
fi

# Create the Docker network if it doesn't exist
echo "Ensuring Docker network exists..."
docker network create safety-event-network 2>/dev/null || echo "Network 'safety-event-network' already exists"

# Build the image
echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container
echo "Starting API container..."
docker run --rm --name $IMAGE_NAME -ti \
    --network safety-event-network \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets \
    -p 9000:9000 \
    -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e GCP_REGION=$GCP_REGION \
    -e CHROMADB_HOST=$CHROMADB_HOST \
    -e CHROMADB_PORT=$CHROMADB_PORT \
    -e ENVIRONMENT=development \
    -e DEBUG=true \
    -e PORT=9000 \
    $IMAGE_NAME
