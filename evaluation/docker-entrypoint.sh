#!/bin/bash

# Safety Event Classification - Evaluation Pipeline Entrypoint
# Initializes the container environment and provides usage instructions

echo "============================================"
echo "Safety Event Classification - Evaluation"
echo "============================================"
echo ""

# Activate virtual environment
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

# Define evaluation command functions
run_evaluation() {
    python evaluate.py "$@"
}

run_evaluation_quick() {
    python evaluate.py --sample-size 10 "$@"
}

run_evaluation_full() {
    python evaluate.py --full "$@"
}

export -f run_evaluation
export -f run_evaluation_quick
export -f run_evaluation_full

# Display usage instructions
echo "============================================"
echo "Usage Instructions:"
echo "============================================"
echo ""
echo "Run Full Evaluation:"
echo "  run_evaluation"
echo "  python evaluate.py"
echo ""
echo "Run Quick Test (10 samples):"
echo "  run_evaluation_quick"
echo "  python evaluate.py --sample-size 10"
echo ""
echo "Run Full Dataset:"
echo "  run_evaluation_full"
echo "  python evaluate.py --full"
echo ""
echo "Available Options:"
echo "  --input FILE      Input CSV file (default: data/performance_evaluation.csv)"
echo "  --output DIR      Output directory for results (default: outputs/)"
echo "  --sample-size N   Number of samples to evaluate (default: all)"
echo "  --full            Run on full dataset (ignores sample-size)"
echo "  --no-rag          Disable RAG context retrieval"
echo "  --verbose         Enable verbose output"
echo ""
echo "============================================"
echo ""

# Execute passed command or keep container running
if [ $# -eq 0 ]; then
    exec /bin/bash
else
    exec "$@"
fi
