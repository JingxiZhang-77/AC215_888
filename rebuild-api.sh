#!/bin/bash

# Rebuild API Service Script
# Use this script when you need to rebuild the API container with fresh dependencies

set -e

echo "============================================"
echo "Rebuilding API Service"
echo "============================================"
echo ""

cd src/api

echo "Step 1: Stopping any running API containers..."
docker stop $(docker ps -q -f name=safety-event-api) 2>/dev/null || true
docker rm $(docker ps -a -q -f name=safety-event-api) 2>/dev/null || true

echo ""
echo "Step 2: Removing old API image..."
docker rmi safety-event-api 2>/dev/null || true

echo ""
echo "Step 3: Building new API image..."
docker build -t safety-event-api -f Dockerfile .

echo ""
echo "============================================"
echo "✅ API rebuild complete!"
echo "============================================"
echo ""
echo "To start the API:"
echo "  cd src/api"
echo "  ./docker-shell.sh"
echo ""
echo "Then inside the container:"
echo "  uvicorn_server"
echo ""
