"""
Safety Event Classification - Model Evaluation Pipeline

This script evaluates the classification model against ground-truth labels.
It computes accuracy, confusion matrix, per-class metrics (precision, recall, F1),
and generates visualization reports.

Usage:
    python evaluate.py                          # Run on full dataset
    python evaluate.py --sample-size 10         # Quick test with 10 samples
    python evaluate.py --input custom.csv       # Use custom input file
    python evaluate.py --verbose                # Enable detailed logging
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import pandas as pd
import numpy as np
from tqdm import tqdm
from tabulate import tabulate

# Scikit-learn for metrics
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Add local api directory to path for imports
# The api/ folder is self-contained within the evaluation directory
API_DIR = os.path.join(os.path.dirname(__file__), "api")
if os.path.isdir(API_DIR) and API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

# Import classification utilities from local api/ directory
try:
    from simple_prompt_utils import (
        prompt1_single_incident,
        prompt2_single_incident,
        prompt3_single_incident,
    )
    PROMPT_UTILS_AVAILABLE = True
except ImportError as exc:
    PROMPT_UTILS_AVAILABLE = False
    print(f"Warning: simple_prompt_utils not available ({exc})")
    print("Make sure the api/ directory exists with simple_prompt_utils.py")

# RAG service is not available in standalone evaluation mode
# Classification will work without RAG context
RAG_AVAILABLE = False
rag_service = None


# Classification labels
CLASSIFICATION_LABELS = {
    "SSE": "Serious Safety Event",
    "PSE": "Precursor Safety Event", 
    "NME": "Near Miss Event",
    "NSE": "No Safety Event"
}

# Valid classification codes (for validation)
VALID_LABELS = ["SSE", "PSE", "NME", "NSE"]

# Department labels
DEPARTMENT_LABELS = {
    "internal medicine": "Internal Medicine",
    "surgery": "Surgery",
    "ob/gyn/nicu": "OB/GYN/NICU",
    "radiology/imaging": "Radiology/Imaging",
    "outpatient/er": "Outpatient/ER",
    "outpatient/ER": "Outpatient/ER",
    "unspecified": "Unspecified"
}


def normalize_department(department: Optional[str]) -> str:
    """Normalize department name to canonical form."""
    if not department or pd.isna(department):
        return "unspecified"
    dept = str(department).strip().lower()
    # Map common variations
    mapping = {
        "internal medicine": "internal medicine",
        "internal_medicine": "internal medicine",
        "surgery": "surgery",
        "ob/gyn/nicu": "ob/gyn/nicu",
        "ob_gyn_nicu": "ob/gyn/nicu",
        "radiology/imaging": "radiology/imaging",
        "radiology_imaging": "radiology/imaging",
        "outpatient/er": "outpatient/ER",
        "outpatient_er": "outpatient/ER",
    }
    return mapping.get(dept, "unspecified")


def classify_single_incident(
    description: str,
    department: Optional[str] = None,
    use_rag: bool = True,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Classify a single incident using the 3-step classification process.
    
    Returns:
        Dictionary with classification_code and step-by-step rationales
    """
    if not PROMPT_UTILS_AVAILABLE:
        raise RuntimeError("Prompt utilities not available. Cannot run classification.")
    
    result = {
        "classification_code": "Unknown",
        "deviation_check": None,
        "deviation_rationale": "",
        "patient_reach_check": None,
        "patient_reach_rationale": "",
        "harm_level_check": None,
        "harm_level_rationale": "",
        "rag_context_used": False,
        "error": None
    }
    
    # Normalize department
    dept = normalize_department(department)
    dept_label = DEPARTMENT_LABELS.get(dept, dept.title()) if dept != "unspecified" else None
    
    try:
        # Retrieve RAG context if available
        policy_context = ""
        if use_rag and RAG_AVAILABLE and rag_service:
            try:
                rag_result = rag_service.retrieve_policy_context(
                    incident_description=description,
                    department=dept,
                    n_results=3
                )
                if rag_result.get("retrieved"):
                    policy_context = rag_result["context"]
                    result["rag_context_used"] = True
            except Exception as e:
                if verbose:
                    print(f"  RAG retrieval failed: {e}")
        
        # Step 1: GAPS deviation check
        gaps_bool, gaps_rationale = prompt1_single_incident(
            description, dept_label, policy_context=policy_context
        )
        result["deviation_check"] = gaps_bool
        result["deviation_rationale"] = gaps_rationale
        
        if not gaps_bool:
            result["classification_code"] = "NSE"
            return result
        
        # Step 2: Reached patient check
        reached_bool, reached_rationale = prompt2_single_incident(
            description, dept_label, policy_context=policy_context
        )
        result["patient_reach_check"] = reached_bool
        result["patient_reach_rationale"] = reached_rationale
        
        if not reached_bool:
            result["classification_code"] = "NME"
            return result
        
        # Step 3: Harm level assessment
        harm_bool, harm_rationale = prompt3_single_incident(
            description, dept_label, policy_context=policy_context
        )
        result["harm_level_check"] = harm_bool
        result["harm_level_rationale"] = harm_rationale
        
        if harm_bool:
            result["classification_code"] = "SSE"
        else:
            result["classification_code"] = "PSE"
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        result["classification_code"] = "Error"
        return result


def load_evaluation_data(input_path: str) -> pd.DataFrame:
    """Load and validate evaluation dataset."""
    print(f"Loading evaluation data from: {input_path}")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Support both CSV and Excel files
    if input_path.endswith('.xlsx') or input_path.endswith('.xls'):
        df = pd.read_excel(input_path)
    else:
        df = pd.read_csv(input_path)
    print(f"  Loaded {len(df)} rows")
    
    # Validate required columns
    required_cols = ["description", "label"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Validate labels
    invalid_labels = df[~df["label"].isin(VALID_LABELS)]["label"].unique()
    if len(invalid_labels) > 0:
        print(f"  Warning: Found invalid labels: {invalid_labels}")
    
    # Clean data
    df = df.dropna(subset=["description", "label"])
    df["description"] = df["description"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip().str.upper()
    
    # Add department column if missing
    if "department" not in df.columns:
        df["department"] = "unspecified"
    
    print(f"  Valid rows after cleaning: {len(df)}")
    print(f"  Label distribution:")
    for label, count in df["label"].value_counts().items():
        print(f"    {label}: {count}")
    
    return df


def run_evaluation(
    df: pd.DataFrame,
    use_rag: bool = True,
    verbose: bool = False
) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Run classification on all samples and collect predictions.
    
    Returns:
        Tuple of (results_df, detailed_results_list)
    """
    predictions = []
    detailed_results = []
    
    print(f"\nRunning classification on {len(df)} samples...")
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Classifying"):
        description = row["description"]
        department = row.get("department", None)
        ground_truth = row["label"]
        
        if verbose:
            print(f"\n[{idx+1}/{len(df)}] Processing incident...")
            print(f"  Department: {department}")
            print(f"  Ground truth: {ground_truth}")
        
        # Classify
        result = classify_single_incident(
            description=description,
            department=department,
            use_rag=use_rag,
            verbose=verbose
        )
        
        prediction = result["classification_code"]
        predictions.append(prediction)
        
        if verbose:
            print(f"  Prediction: {prediction}")
            if prediction != ground_truth:
                print(f"  ❌ MISMATCH!")
        
        # Store detailed result
        detailed_results.append({
            "index": idx,
            "description": description[:200] + "..." if len(description) > 200 else description,
            "department": department,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "correct": prediction == ground_truth,
            "deviation_check": result["deviation_check"],
            "deviation_rationale": result["deviation_rationale"],
            "patient_reach_check": result["patient_reach_check"],
            "patient_reach_rationale": result["patient_reach_rationale"],
            "harm_level_check": result["harm_level_check"],
            "harm_level_rationale": result["harm_level_rationale"],
            "rag_context_used": result["rag_context_used"],
            "error": result["error"]
        })
    
    # Add predictions to dataframe
    results_df = df.copy()
    results_df["prediction"] = predictions
    results_df["correct"] = results_df["label"] == results_df["prediction"]
    
    return results_df, detailed_results


def compute_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Compute classification metrics."""
    # Filter out error predictions
    valid_mask = [p in VALID_LABELS for p in y_pred]
    y_true_valid = [y for y, m in zip(y_true, valid_mask) if m]
    y_pred_valid = [p for p, m in zip(y_pred, valid_mask) if m]
    
    if len(y_true_valid) == 0:
        return {"error": "No valid predictions to evaluate"}
    
    # Overall metrics
    accuracy = accuracy_score(y_true_valid, y_pred_valid)
    
    # Per-class metrics
    precision_macro = precision_score(y_true_valid, y_pred_valid, labels=VALID_LABELS, average="macro", zero_division=0)
    recall_macro = recall_score(y_true_valid, y_pred_valid, labels=VALID_LABELS, average="macro", zero_division=0)
    f1_macro = f1_score(y_true_valid, y_pred_valid, labels=VALID_LABELS, average="macro", zero_division=0)
    
    precision_weighted = precision_score(y_true_valid, y_pred_valid, labels=VALID_LABELS, average="weighted", zero_division=0)
    recall_weighted = recall_score(y_true_valid, y_pred_valid, labels=VALID_LABELS, average="weighted", zero_division=0)
    f1_weighted = f1_score(y_true_valid, y_pred_valid, labels=VALID_LABELS, average="weighted", zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_true_valid, y_pred_valid, labels=VALID_LABELS)
    
    # Per-class detailed metrics
    class_report = classification_report(
        y_true_valid, y_pred_valid, 
        labels=VALID_LABELS, 
        target_names=[CLASSIFICATION_LABELS[l] for l in VALID_LABELS],
        output_dict=True,
        zero_division=0
    )
    
    return {
        "total_samples": len(y_true),
        "valid_predictions": len(y_true_valid),
        "error_predictions": len(y_true) - len(y_true_valid),
        "accuracy": accuracy,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "precision_weighted": precision_weighted,
        "recall_weighted": recall_weighted,
        "f1_weighted": f1_weighted,
        "confusion_matrix": cm.tolist(),
        "classification_report": class_report
    }


def plot_confusion_matrix(cm: np.ndarray, output_path: str):
    """Generate and save confusion matrix heatmap."""
    plt.figure(figsize=(10, 8))
    
    # Create labels
    labels = [CLASSIFICATION_LABELS[l] for l in VALID_LABELS]
    
    # Plot heatmap
    sns.heatmap(
        cm, 
        annot=True, 
        fmt="d", 
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        square=True,
        cbar_kws={"shrink": 0.8}
    )
    
    plt.xlabel("Predicted", fontsize=12)
    plt.ylabel("Ground Truth", fontsize=12)
    plt.title("Confusion Matrix - Safety Event Classification", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Confusion matrix saved to: {output_path}")


def plot_per_class_metrics(class_report: Dict, output_path: str):
    """Generate and save per-class metrics bar chart."""
    # Extract per-class metrics
    classes = []
    precision_vals = []
    recall_vals = []
    f1_vals = []
    
    for label in VALID_LABELS:
        label_name = CLASSIFICATION_LABELS[label]
        if label_name in class_report:
            classes.append(label)
            precision_vals.append(class_report[label_name]["precision"])
            recall_vals.append(class_report[label_name]["recall"])
            f1_vals.append(class_report[label_name]["f1-score"])
    
    x = np.arange(len(classes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width, precision_vals, width, label="Precision", color="#2196F3")
    bars2 = ax.bar(x, recall_vals, width, label="Recall", color="#4CAF50")
    bars3 = ax.bar(x + width, f1_vals, width, label="F1-Score", color="#FF9800")
    
    ax.set_xlabel("Classification", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Per-Class Performance Metrics", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([CLASSIFICATION_LABELS[c] for c in classes], rotation=15, ha="right")
    ax.legend()
    ax.set_ylim(0, 1.1)
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Per-class metrics chart saved to: {output_path}")


def generate_report(
    metrics: Dict[str, Any],
    detailed_results: List[Dict],
    output_dir: str,
    timestamp: str
) -> str:
    """Generate comprehensive evaluation report."""
    
    report_lines = [
        "=" * 70,
        "SAFETY EVENT CLASSIFICATION - MODEL EVALUATION REPORT",
        "=" * 70,
        f"Generated: {timestamp}",
        "",
        "-" * 70,
        "OVERALL METRICS",
        "-" * 70,
        f"Total Samples:        {metrics['total_samples']}",
        f"Valid Predictions:    {metrics['valid_predictions']}",
        f"Error Predictions:    {metrics['error_predictions']}",
        "",
        f"Accuracy:             {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)",
        "",
        "Macro-Averaged Metrics:",
        f"  Precision:          {metrics['precision_macro']:.4f}",
        f"  Recall:             {metrics['recall_macro']:.4f}",
        f"  F1-Score:           {metrics['f1_macro']:.4f}",
        "",
        "Weighted-Averaged Metrics:",
        f"  Precision:          {metrics['precision_weighted']:.4f}",
        f"  Recall:             {metrics['recall_weighted']:.4f}",
        f"  F1-Score:           {metrics['f1_weighted']:.4f}",
        "",
        "-" * 70,
        "PER-CLASS PERFORMANCE",
        "-" * 70,
    ]
    
    # Per-class table
    class_data = []
    for label in VALID_LABELS:
        label_name = CLASSIFICATION_LABELS[label]
        if label_name in metrics["classification_report"]:
            stats = metrics["classification_report"][label_name]
            class_data.append([
                label,
                label_name,
                f"{stats['precision']:.4f}",
                f"{stats['recall']:.4f}",
                f"{stats['f1-score']:.4f}",
                int(stats['support'])
            ])
    
    table = tabulate(
        class_data,
        headers=["Code", "Classification", "Precision", "Recall", "F1-Score", "Support"],
        tablefmt="grid"
    )
    report_lines.append(table)
    
    # Confusion matrix
    report_lines.extend([
        "",
        "-" * 70,
        "CONFUSION MATRIX",
        "-" * 70,
        "Rows: Ground Truth, Columns: Predictions",
        ""
    ])
    
    cm = np.array(metrics["confusion_matrix"])
    cm_table = tabulate(
        [[VALID_LABELS[i]] + list(row) for i, row in enumerate(cm)],
        headers=[""] + VALID_LABELS,
        tablefmt="grid"
    )
    report_lines.append(cm_table)
    
    # Misclassification analysis
    misclassified = [r for r in detailed_results if not r["correct"] and r["prediction"] != "Error"]
    if misclassified:
        report_lines.extend([
            "",
            "-" * 70,
            f"MISCLASSIFICATION ANALYSIS ({len(misclassified)} errors)",
            "-" * 70,
        ])
        
        for i, mc in enumerate(misclassified[:10]):  # Show first 10
            report_lines.extend([
                f"\n[Error {i+1}]",
                f"  Ground Truth: {mc['ground_truth']}",
                f"  Prediction:   {mc['prediction']}",
                f"  Department:   {mc['department']}",
                f"  Description:  {mc['description'][:150]}...",
                f"  Step Analysis:",
                f"    - Deviation from GAPS: {mc['deviation_check']}",
                f"    - Reached Patient:     {mc['patient_reach_check']}",
                f"    - Caused Harm:         {mc['harm_level_check']}",
            ])
        
        if len(misclassified) > 10:
            report_lines.append(f"\n  ... and {len(misclassified) - 10} more errors (see detailed CSV)")
    
    report_lines.extend([
        "",
        "=" * 70,
        "END OF REPORT",
        "=" * 70
    ])
    
    report_text = "\n".join(report_lines)
    
    # Save report
    report_path = os.path.join(output_dir, f"evaluation_report_{timestamp}.txt")
    with open(report_path, "w") as f:
        f.write(report_text)
    print(f"  Report saved to: {report_path}")
    
    return report_text


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Safety Event Classification Model"
    )
    parser.add_argument(
        "--input", "-i",
        default="data/performance_evaluation.xlsx",
        help="Input CSV or Excel file with ground truth labels"
    )
    parser.add_argument(
        "--output", "-o",
        default="outputs",
        help="Output directory for results"
    )
    parser.add_argument(
        "--sample-size", "-n",
        type=int,
        default=None,
        help="Number of samples to evaluate (default: all)"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Run on full dataset (ignores sample-size)"
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable RAG context retrieval"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not PROMPT_UTILS_AVAILABLE:
        print("ERROR: Classification utilities not available.")
        print("Please ensure you're running inside the Docker container.")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "=" * 60)
    print("SAFETY EVENT CLASSIFICATION - MODEL EVALUATION")
    print("=" * 60)
    
    # Load data
    df = load_evaluation_data(args.input)
    
    # Sample if requested
    if not args.full and args.sample_size is not None:
        if args.sample_size < len(df):
            print(f"\nSampling {args.sample_size} rows from {len(df)} total...")
            df = df.sample(n=args.sample_size, random_state=42)
    
    # Run evaluation
    use_rag = not args.no_rag
    print(f"\nRAG Context: {'Enabled' if use_rag else 'Disabled'}")
    
    results_df, detailed_results = run_evaluation(
        df=df,
        use_rag=use_rag,
        verbose=args.verbose
    )
    
    # Compute metrics
    print("\nComputing metrics...")
    metrics = compute_metrics(
        y_true=results_df["label"].tolist(),
        y_pred=results_df["prediction"].tolist()
    )
    
    if "error" in metrics:
        print(f"ERROR: {metrics['error']}")
        sys.exit(1)
    
    # Print summary
    print("\n" + "-" * 60)
    print("EVALUATION RESULTS SUMMARY")
    print("-" * 60)
    print(f"Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"F1 (Macro): {metrics['f1_macro']:.4f}")
    print(f"F1 (Weighted): {metrics['f1_weighted']:.4f}")
    
    # Generate outputs
    print("\nGenerating outputs...")
    
    # Save detailed results CSV
    results_csv_path = os.path.join(args.output, f"evaluation_results_{timestamp}.csv")
    results_df.to_csv(results_csv_path, index=False)
    print(f"  Detailed results saved to: {results_csv_path}")
    
    # Save metrics JSON
    metrics_json_path = os.path.join(args.output, f"metrics_{timestamp}.json")
    with open(metrics_json_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics JSON saved to: {metrics_json_path}")
    
    # Generate plots
    cm_path = os.path.join(args.output, f"confusion_matrix_{timestamp}.png")
    plot_confusion_matrix(np.array(metrics["confusion_matrix"]), cm_path)
    
    class_metrics_path = os.path.join(args.output, f"per_class_metrics_{timestamp}.png")
    plot_per_class_metrics(metrics["classification_report"], class_metrics_path)
    
    # Generate text report
    report_text = generate_report(metrics, detailed_results, args.output, timestamp)
    
    # Print report to console
    print("\n" + report_text)
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
