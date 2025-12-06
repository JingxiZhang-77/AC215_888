#!/bin/bash

# Test runner script for Safety Event Classification API
# Usage: ./run-tests.sh [unit|integration|system|all|coverage|build]
# Following cheese-app-ci-cd reference pattern for Docker-based testing.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")"

IMAGE_NAME="safety-event-api:local"

echo -e "${YELLOW}Docker-based Test Runner${NC}"
echo -e "${YELLOW}========================${NC}"

# Build image if it doesn't exist or if build is requested
build_image() {
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build -t ${IMAGE_NAME} -f Dockerfile.test .
}

case "${1:-all}" in
    build)
        build_image
        echo -e "${GREEN}Image built successfully!${NC}"
        ;;
    unit)
        echo -e "${GREEN}Running Unit Tests...${NC}"
        docker run --rm ${IMAGE_NAME} pytest tests/unit/ -v --tb=short
        ;;
    integration)
        echo -e "${GREEN}Running Integration Tests...${NC}"
        docker run --rm -v "$(pwd)/secrets:/secrets:ro" ${IMAGE_NAME} pytest tests/integration/ -v --tb=short
        ;;
    system)
        echo -e "${GREEN}Running System Tests...${NC}"
        echo -e "${YELLOW}Note: API must be running at localhost:9000${NC}"
        docker run --rm --network host ${IMAGE_NAME} pytest tests/system/ -v --tb=short
        ;;
    coverage)
        echo -e "${GREEN}Running All Tests with Coverage...${NC}"
        docker run --rm -v "$(pwd)/secrets:/secrets:ro" ${IMAGE_NAME} pytest tests/unit/ tests/integration/ \
            --cov=utils --cov=routers --cov=services --cov=models \
            --cov-report=term-missing \
            --cov-fail-under=50
        ;;
    all)
        echo -e "${GREEN}Running All Tests (excluding system tests)...${NC}"
        docker run --rm -v "$(pwd)/secrets:/secrets:ro" ${IMAGE_NAME} pytest tests/unit/ tests/integration/ -v --tb=short
        ;;
    all-with-system)
        echo -e "${GREEN}Running All Tests (including system tests)...${NC}"
        echo -e "${YELLOW}Note: API must be running at localhost:9000${NC}"
        docker run --rm --network host -v "$(pwd)/secrets:/secrets:ro" ${IMAGE_NAME} pytest tests/ -v --tb=short
        ;;
    *)
        echo "Usage: $0 [build|unit|integration|system|all|coverage|all-with-system]"
        echo ""
        echo "  build           - Build the Docker test image"
        echo "  unit            - Run unit tests only"
        echo "  integration     - Run integration tests only"
        echo "  system          - Run system tests (requires running API)"
        echo "  all             - Run all tests except system tests"
        echo "  coverage        - Run tests with coverage report"
        echo "  all-with-system - Run all tests including system tests"
        echo ""
        echo "Example workflow:"
        echo "  ./run-tests.sh build        # Build image once"
        echo "  ./run-tests.sh unit         # Run unit tests"
        echo "  ./run-tests.sh coverage     # Run with coverage"
        exit 1
        ;;
esac

echo -e "${GREEN}Done!${NC}"
