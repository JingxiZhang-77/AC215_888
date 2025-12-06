# Safety Event Classification - Evaluation Pipeline

This module provides a comprehensive evaluation pipeline for measuring the performance of the Safety Event Classification model against ground-truth labeled data.

## Overview

The evaluation pipeline:
1. Loads labeled evaluation data from CSV
2. Runs the 3-step classification process on each incident
3. Compares predictions against ground-truth labels
4. Computes accuracy, precision, recall, F1-score, and confusion matrix
5. Generates detailed reports and visualizations

## Directory Structure

```
evaluation/
├── data/
│   └── performance_evaluation.csv   # Ground truth labeled data
├── outputs/                         # Generated results (created automatically)
│   ├── evaluation_results_*.csv     # Detailed results per sample
│   ├── metrics_*.json               # Metrics in JSON format
│   ├── confusion_matrix_*.png       # Confusion matrix visualization
│   ├── per_class_metrics_*.png      # Per-class performance chart
│   └── evaluation_report_*.txt      # Full text report
├── Dockerfile
├── docker-shell.sh
├── docker-entrypoint.sh
├── evaluate.py                      # Main evaluation script
├── pyproject.toml
└── README.md
```

## Quick Start

### 1. Build and Start the Container

```bash
cd evaluation
chmod +x docker-shell.sh
./docker-shell.sh
```

### 2. Run Evaluation

Inside the container:

```bash
# Run full evaluation on all samples
run_evaluation

# Or quick test with 10 samples
run_evaluation_quick

# Or use Python directly
python evaluate.py --help
```

## Data Format

The input CSV file must contain the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| `description` | Yes | Incident description text |
| `label` | Yes | Ground truth classification (SSE, PSE, NME, NSE) |
| `department` | No | Department name (optional, defaults to "unspecified") |

### Classification Codes

| Code | Classification | Description |
|------|----------------|-------------|
| SSE | Serious Safety Event | Deviation reached patient, caused moderate/severe harm or death |
| PSE | Precursor Safety Event | Deviation reached patient, no or minimal harm |
| NME | Near Miss Event | Deviation occurred but did not reach patient |
| NSE | No Safety Event | No deviation from Generally Accepted Performance Standards |

## Command Line Options

```bash
python evaluate.py [OPTIONS]

Options:
  --input, -i FILE      Input CSV file (default: data/performance_evaluation.csv)
  --output, -o DIR      Output directory for results (default: outputs/)
  --sample-size, -n N   Number of samples to evaluate (default: all)
  --full, -f            Run on full dataset (ignores sample-size)
  --no-rag              Disable RAG context retrieval
  --verbose, -v         Enable verbose output with per-sample details
```

## Examples

```bash
# Full evaluation
python evaluate.py

# Quick test with 10 samples
python evaluate.py --sample-size 10

# Custom input file
python evaluate.py --input data/custom_test.csv

# Disable RAG context (faster, but may affect accuracy)
python evaluate.py --no-rag

# Verbose mode for debugging
python evaluate.py --sample-size 5 --verbose
```

## Output Files

After running evaluation, the following files are generated in the `outputs/` directory:

### 1. `evaluation_results_*.csv`
Detailed results for each sample including:
- Original description and department
- Ground truth label
- Predicted label
- Whether prediction was correct
- Step-by-step rationales

### 2. `metrics_*.json`
All computed metrics in JSON format:
- Accuracy
- Precision, Recall, F1 (macro and weighted)
- Confusion matrix
- Per-class statistics

### 3. `confusion_matrix_*.png`
Visual heatmap of the confusion matrix showing prediction patterns.

### 4. `per_class_metrics_*.png`
Bar chart comparing precision, recall, and F1-score for each classification.

### 5. `evaluation_report_*.txt`
Comprehensive text report including:
- Overall metrics summary
- Per-class performance table
- Confusion matrix
- Misclassification analysis

## Metrics Explained

### Accuracy
Overall percentage of correct predictions.

### Precision
For each class, the proportion of predicted positives that are correct.
- High precision = few false positives

### Recall
For each class, the proportion of actual positives that were correctly identified.
- High recall = few false negatives

### F1-Score
Harmonic mean of precision and recall, balancing both metrics.

### Macro vs Weighted Average
- **Macro**: Simple average across all classes (treats all classes equally)
- **Weighted**: Average weighted by class support (accounts for class imbalance)

## Requirements

The evaluation pipeline requires:
- Google Cloud credentials for LLM access
- Optional: ChromaDB connection for RAG context

These are configured automatically when running inside the Docker container.

## Troubleshooting

### "Prompt utilities not available"
Ensure you're running inside the Docker container with proper environment setup.

### "Google Cloud credentials not found"
Make sure `llm-service-account.json` exists in the `secrets/` directory.

### RAG context not available
RAG is optional. The evaluation will work without it, but accuracy may differ from production.
