#!/bin/bash

echo "============================================"
echo "Data Pipeline - Synthetic Data Generation"
echo "============================================"
echo ""

# Check for GCP credentials
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "WARNING: GCP credentials not found at $GOOGLE_APPLICATION_CREDENTIALS"
    echo "Please ensure the secrets volume is mounted correctly."
    echo ""
fi

# Display environment info
echo "Environment:"
echo "  Python: $(python --version 2>&1)"
echo "  Working Directory: $(pwd)"
echo "  GCP Project: ${GCP_PROJECT:-not set}"
echo "  GCP Region: ${GCP_REGION:-not set}"
echo ""

# Display usage instructions
echo "Usage:"
echo "  python data_generation.py [OPTIONS]"
echo ""
echo "Options:"
echo "  --num_samples N     Number of samples to generate (default: 10)"
echo "  --output_file PATH  Output file path (default: outputs/generated_incidents.csv)"
echo ""
echo "Example:"
echo "  python data_generation.py --num_samples 50"
echo "  python data_generation.py --num_samples 100 --output_file outputs/large_dataset.csv"
echo ""
echo "============================================"
echo ""

# Start interactive shell
exec /bin/bash
