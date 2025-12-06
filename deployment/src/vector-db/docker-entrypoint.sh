#!/bin/bash

echo "============================================"
echo "Safety Event Classification - Vector DB"
echo "============================================"
echo "Container is running!"
echo "Architecture: $(uname -m)"

# Activate virtual environment
echo "Activating virtual environment..."
source /.venv/bin/activate

echo "Environment ready! Virtual environment activated."
echo "Python version: $(python --version)"
echo "UV version: $(uv --version)"
echo ""
echo "============================================"
echo "Usage Instructions:"
echo "============================================"
echo ""
echo "Process Policy Documents:"
echo "  python cli.py --chunk --chunk_type char-split"
echo "  python cli.py --embed --chunk_type char-split"
echo "  python cli.py --load --chunk_type char-split"
echo ""
echo "Test Query:"
echo "  python cli.py --query --chunk_type char-split --department internal_medicine"
echo ""
echo "ChromaDB Connection:"
echo "  Host: ${CHROMADB_HOST:-localhost}"
echo "  Port: ${CHROMADB_PORT:-8000}"
echo ""
echo "Available Departments:"
echo "  - internal_medicine (Medicine.txt)"
echo "  - surgery (Surgery.txt)"
echo "  - ob_gyn_nicu (OB_GYN_NICU.txt)"
echo "  - radiology_imaging (Radiology_Imaging.txt)"
echo "  - outpatient_er (Outpatient_ER.txt)"
echo ""
echo "============================================"
echo ""

# Keep a shell open
exec /bin/bash
