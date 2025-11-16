#!/bin/bash

# Exit on any error
set -e

echo "=== Safety Event Classification System - Frontend ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -q -r requirements.txt

# Check for service account file
SERVICE_ACCOUNT="../../../secrets/llm-service-account.json"
if [ ! -f "$SERVICE_ACCOUNT" ]; then
    echo "WARNING: Service account file not found at $SERVICE_ACCOUNT"
    echo "Please ensure your GCP credentials are properly configured."
    echo ""
fi

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT"

echo ""
echo "Starting Flask application..."
echo "Access the application at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py
