#!/bin/bash

# Safety Event Classification API - Docker Entrypoint
# Initializes the container environment and provides usage instructions

echo "============================================"
echo "Safety Event Classification API"
echo "============================================"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Display environment information
echo "Environment Information:"
echo "  Python: $(python --version)"
echo "  UV: $(uv --version)"
echo "  Working Directory: $(pwd)"
echo ""

# Check for Google Cloud credentials
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "✓ Google Cloud credentials found"
else
    echo "⚠ Google Cloud credentials not found at: $GOOGLE_APPLICATION_CREDENTIALS"
fi
echo ""

# Display usage instructions
echo "============================================"
echo "Usage Instructions:"
echo "============================================"
echo ""
echo "Start API Server:"
echo "  uvicorn main:app --host 0.0.0.0 --port 9000 --reload"
echo ""
echo "Or using Python:"
echo "  python main.py"
echo ""
echo "API Documentation:"
echo "  http://localhost:9000/api/docs (Swagger UI)"
echo "  http://localhost:9000/api/redoc (ReDoc)"
echo ""
echo "Available Scripts:"
echo "  python main.py              - Start API server"
echo "  pytest                      - Run tests"
echo ""
echo "============================================"
echo ""

# Keep container running
exec /bin/bash
