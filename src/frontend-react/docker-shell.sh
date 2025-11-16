#!/bin/bash

# Exit on error
set -e

# Set image name
export IMAGE_NAME="safety-event-frontend-react"
export BASE_DIR=$(pwd)

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-p 3001:3001 \
$IMAGE_NAME
