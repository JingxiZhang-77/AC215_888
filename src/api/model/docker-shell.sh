#!/bin/bash

# Define some environment variables
export IMAGE_NAME="prompt_chaining"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container with the necessary volume mounts and environment variables
docker run --rm -it \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS" \
    "$IMAGE_NAME"