#!/bin/bash

echo "Container is running!!!"
echo "Architecture: $(uname -m)"

# Activate virtual environment
echo "Activating virtual environment..."
source /home/app/.venv/bin/activate

echo "Environment ready! Virtual environment activated."
echo "Python version: $(python --version)"
echo "UV version: $(uv --version)"

# Display available scripts
echo ""
echo "==================================="
echo "Data Pipeline Environment Ready"
echo "==================================="
echo "Available Python scripts:"
echo "  - data_generation.py"
echo ""
echo "Example usage:"
echo "  python data_generation.py"
echo ""

# Keep a shell open
exec /bin/bash
