#!/bin/bash

# Exit on any error
set -e

# Set variables
IMAGE_NAME="safety-event-frontend"
CONTAINER_NAME="safety-event-frontend-dev"
PORT=8080

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Stop and remove existing container if it exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping and removing existing container..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
fi

# Run the container
echo "Starting container..."
docker run -it --rm \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    -v "$(pwd)":/app \
    -v "$(pwd)/../model":/app/model \
    -v "$(pwd)/../../secrets/llm-service-account.json":/app/secrets/llm-service-account.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/llm-service-account.json \
    $IMAGE_NAME

echo "Container stopped."
