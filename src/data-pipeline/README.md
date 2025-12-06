# Data Pipeline - Synthetic Incident Generator

This module generates synthetic hospital safety incident data using LLM for training and evaluation of the Safety Event Classification model.

## Overview

The data pipeline uses Google's Gemini model to generate realistic medical safety incidents across different:
- **Severity levels**: SSE, PSE, NME, NSE
- **Departments**: Internal Medicine, Surgery, OB/GYN/NICU, Radiology/Imaging, Outpatient/ER

## Directory Structure

```
data-pipeline/
├── data_generation.py      # Main generation script
├── Dockerfile              # Container definition
├── docker-shell.sh         # Build and run script
├── docker-entrypoint.sh    # Container initialization
├── pyproject.toml          # Python dependencies
├── README.md               # This file
└── outputs/                # Generated data (created automatically)
    ├── raw_response.txt           # Raw LLM response
    ├── medical_incidents.xlsx     # Latest structured output
    └── medical_incidents_*.xlsx   # Timestamped outputs
```

## Quick Start

### 1. Build and Start the Container

```bash
cd src/data-pipeline
chmod +x docker-shell.sh
./docker-shell.sh
```

### 2. Generate Data

Inside the container:

```bash
# Generate 5 incidents (default)
generate_data

# Generate custom number of incidents
generate_data --num_generate 20

# Or use the batch helper
generate_data_batch 50
```

## Command Line Options

```bash
python data_generation.py [OPTIONS]

Options:
  --num_generate, -n INT   Number of incidents to generate (default: 5)
  --output, -o DIR         Output directory (default: outputs)
```

## Output Files

| File | Description |
|------|-------------|
| `raw_response.txt` | Raw text response from the LLM |
| `medical_incidents.xlsx` | Latest structured data with Department and Description columns |
| `medical_incidents_YYYYMMDD_HHMMSS.xlsx` | Timestamped version for tracking |

## Output Format

The generated Excel file contains:

| Column | Description |
|--------|-------------|
| `Department` | Hospital department (Internal Medicine, Surgery, etc.) |
| `Incident Description` | Detailed incident description (60+ words) |

## Requirements

- Google Cloud credentials with Vertex AI access
- `llm-service-account.json` in the `secrets/` directory

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GCP_PROJECT` | apcomp215-group88 | Google Cloud project ID |
| `GCP_REGION` | us-central1 | Google Cloud region |
| `GOOGLE_APPLICATION_CREDENTIALS` | /secrets/llm-service-account.json | Path to service account |

## Example Usage

```bash
# Generate a small test batch
python data_generation.py --num_generate 5

# Generate a larger dataset for training
python data_generation.py --num_generate 100 --output outputs/training_data

# Generate evaluation data
python data_generation.py --num_generate 50 --output outputs/eval_data
```

## Troubleshooting

### "Google Cloud credentials not found"
Ensure `llm-service-account.json` exists in the `secrets/` directory at the repository root.

### "Could not parse structured data"
The LLM response didn't match the expected format. Check `outputs/raw_response.txt` for the actual response.
