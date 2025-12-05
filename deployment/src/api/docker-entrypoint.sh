#!/bin/bash

# Safety Event Classification API - Docker Entrypoint
# Initializes the container environment and provides usage instructions

echo "============================================"
echo "Safety Event Classification API"
echo "============================================"
echo ""

# Activate virtual environment (absolute path)
source /home/app/.venv/bin/activate

# Display environment information
echo "Environment Information:"
echo "  Python: $(python --version)"
echo "  UV: $(uv --version)"
echo "  Working Directory: $(pwd)"
echo "  Virtual Env: $(which python)"
echo ""

# Check for Google Cloud credentials
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "✓ Google Cloud credentials found"
else
    echo "⚠ Google Cloud credentials not found at: $GOOGLE_APPLICATION_CREDENTIALS"
fi
echo ""

# Define uvicorn_server command function
uvicorn_server() {
    uvicorn service:app --host 0.0.0.0 --port 9000 --log-level info --reload "$@"
}

uvicorn_server_production() {
    uvicorn service:app --host 0.0.0.0 --port 9000 --lifespan on "$@"
}

export -f uvicorn_server
export -f uvicorn_server_production

# Display usage instructions
echo "============================================"
echo "Usage Instructions:"
echo "============================================"
echo ""
echo "Start API Server (Development):"
echo "  uvicorn_server"
echo ""
echo "Start API Server (Production):"
echo "  uvicorn_server_production"
echo ""
echo "API Documentation:"
echo "  http://localhost:9000/api/docs (Swagger UI)"
echo "  http://localhost:9000/api/redoc (ReDoc)"
echo ""
echo "Available Commands:"
echo "  uvicorn_server              - Start development server with auto-reload"
echo "  uvicorn_server_production   - Start production server"
echo "  pytest                      - Run tests"
echo ""
echo "============================================"
echo ""

# Execute passed command or keep container running
if [ $# -eq 0 ]; then
    exec /bin/bash
else
    exec "$@"
fi
