#!/bin/bash

# Define some environment variables
export IMAGE_NAME="audio-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json
export GCP_PROJECT="apcomp215-group88"
export GCP_LOCATION="us-central1"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container with the necessary volume mounts and environment variables
docker run --rm -it \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS" \
    -e GCP_PROJECT="$GCP_PROJECT" \
    -e GCP_LOCATION="$GCP_LOCATION" \
    "$IMAGE_NAME"
