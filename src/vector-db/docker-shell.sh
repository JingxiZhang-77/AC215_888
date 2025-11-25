#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Set variables
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export GCP_PROJECT="apcomp215-group88"
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/llm-service-account.json"
export IMAGE_NAME="safety-vector-db-cli"

# Create the network if we don't have it yet
docker network inspect safety-event-network >/dev/null 2>&1 || docker network create safety-event-network

# Build the image based on the Dockerfile
echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME -f Dockerfile .

# Run All Containers (this will start ChromaDB automatically)
echo "Starting Vector DB and ChromaDB containers..."
docker-compose run --rm --service-ports $IMAGE_NAME
