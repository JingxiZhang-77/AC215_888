#!/bin/bash

# Test runner script for Safety Event Classification API
# Usage: ./run-tests.sh [unit|integration|system|all|coverage]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to API directory
cd "$(dirname "$0")/../api"

echo -e "${YELLOW}Running tests from: $(pwd)${NC}"

# Ensure we're in a virtual environment or have dependencies
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    uv venv
    uv sync --dev
fi

# Activate venv
source .venv/bin/activate

# Copy tests into API directory for path resolution
if [ ! -d "tests" ]; then
    echo -e "${YELLOW}Linking tests directory...${NC}"
    ln -sf ../tests tests
fi

case "${1:-all}" in
    unit)
        echo -e "${GREEN}Running Unit Tests...${NC}"
        pytest tests/unit/ -v --tb=short
        ;;
    integration)
        echo -e "${GREEN}Running Integration Tests...${NC}"
        pytest tests/integration/ -v --tb=short
        ;;
    system)
        echo -e "${GREEN}Running System Tests...${NC}"
        echo -e "${YELLOW}Note: API must be running at localhost:9000${NC}"
        pytest tests/system/ -v --tb=short
        ;;
    coverage)
        echo -e "${GREEN}Running All Tests with Coverage...${NC}"
        pytest tests/unit/ tests/integration/ \
            --cov=utils --cov=routers --cov=services --cov=models \
            --cov-report=term-missing \
            --cov-report=html:htmlcov \
            --cov-fail-under=50
        echo -e "${GREEN}Coverage report generated in htmlcov/${NC}"
        ;;
    all)
        echo -e "${GREEN}Running All Tests...${NC}"
        pytest tests/ -v --tb=short --ignore=tests/system/
        ;;
    *)
        echo "Usage: $0 [unit|integration|system|all|coverage]"
        echo ""
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  system      - Run system tests (requires running API)"
        echo "  coverage    - Run tests with coverage report"
        echo "  all         - Run unit and integration tests (default)"
        exit 1
        ;;
esac

echo -e "${GREEN}Tests completed!${NC}"
