import os 
import pandas as pd
import json
import argparse
from prompt_utils import (
    prompt1_single_incident,
    prompt2_single_incident,
    prompt3_single_incident
)

BASE_DIR = os.path.join(os.path.dirname(__file__))  
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

DEFAULT_INPUT_FILE = os.path.join(BASE_DIR, "prompt_tests", "prompt_chaining_test.xlsx")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "chaining_output.csv")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "chaining_output.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Valid departments
VALID_DEPARTMENTS = [
    "internal medicine",
    "surgery",
    "ob/gyn/nicu",
    "radiology/imaging",
    "outpatient/ER"
]

def process_incidents_rowwise(df: pd.DataFrame, default_department: str = None) -> pd.DataFrame:
    """
    Process incidents in DataFrame one-by-one, running prompt chain with per-incident branching.
    
    Args:
        df: DataFrame with incident data
        default_department: Default department if not specified in data
    
    Returns:
        DataFrame with classification results including department
    """
    results = []
    for i, row in df.iterrows():
        incident_description = row["Brief Factual Description"]
        
        # Get department from row or use default
        department = row.get("Department", default_department) if "Department" in df.columns else default_department
        if department and department.lower() not in VALID_DEPARTMENTS:
            department = "unspecified"
        elif department:
            department = department.lower()

        # Initialize
        gaps_deviation_ans = 'N/A'
        reached_patient_ans = 'N/A'
        harm_level_ans = 'N/A'
        final_classification = 'Unknown'
        rationale_text = 'N/A'

        # ---- Step 1: GAPS deviation check ----
        try:
            gaps_deviation_bool = prompt1_single_incident(incident_description)
            gaps_deviation_ans = "Yes" if gaps_deviation_bool else "No"
        except Exception as e:
            rationale_text = f"Error in prompt 1: {e}"
            results.append({
                "incident": incident_description,
                "department": department,
                "gaps_deviation_check": gaps_deviation_ans,
                "reached_patient_check": reached_patient_ans,
                "harm_level_check": harm_level_ans,
                "final_classification_code": final_classification,
                "rationale": rationale_text
            })
            continue

        if not gaps_deviation_bool:
            final_classification = "NSE"
            rationale_text = "No deviation from Generally Accepted Performance Standards (GAPS)."
            results.append({
                "incident": incident_description,
                "department": department,
                "gaps_deviation_check": gaps_deviation_ans,
                "reached_patient_check": reached_patient_ans,
                "harm_level_check": harm_level_ans,
                "final_classification_code": final_classification,
                "rationale": rationale_text
            })
            continue

        # ---- Step 2: Reached patient check ----
        try:
            reached_patient_bool = prompt2_single_incident(incident_description)
            reached_patient_ans = "Yes" if reached_patient_bool else "No"
        except Exception as e:
            rationale_text = f"Error in prompt 2: {e}"
            results.append({
                "incident": incident_description,
                "department": department,
                "gaps_deviation_check": gaps_deviation_ans,
                "reached_patient_check": reached_patient_ans,
                "harm_level_check": harm_level_ans,
                "final_classification_code": final_classification,
                "rationale": rationale_text
            })
            continue

        if not reached_patient_bool:
            final_classification = "NME"
            rationale_text = "Deviation occurred but did not reach the patient."
            results.append({
                "incident": incident_description,
                "department": department,
                "gaps_deviation_check": gaps_deviation_ans,
                "reached_patient_check": reached_patient_ans,
                "harm_level_check": harm_level_ans,
                "final_classification_code": final_classification,
                "rationale": rationale_text
            })
            continue

        # ---- Step 3: Harm level check ----
        try:
            harm_level_bool = prompt3_single_incident(incident_description)
            harm_level_ans = "Yes" if harm_level_bool else "No"
        except Exception as e:
            rationale_text = f"Error in prompt 3: {e}"
            results.append({
                "incident": incident_description,
                "department": department,
                "gaps_deviation_check": gaps_deviation_ans,
                "reached_patient_check": reached_patient_ans,
                "harm_level_check": harm_level_ans,
                "final_classification_code": final_classification,
                "rationale": rationale_text
            })
            continue

        if harm_level_bool:
            final_classification = "SSE"
            rationale_text = "Deviation reached the patient and caused moderate/severe harm or death."
        else:
            final_classification = "PSE"
            rationale_text = "Deviation reached the patient with no or minimal harm."

        results.append({
            "incident": incident_description,
            "department": department,
            "gaps_deviation_check": gaps_deviation_ans,
            "reached_patient_check": reached_patient_ans,
            "harm_level_check": harm_level_ans,
            "final_classification_code": final_classification,
            "rationale": rationale_text
        })

    return pd.DataFrame(results)

def main(input_file: str, department: str = None) -> None:
    """
    Main function to process incidents from file
    
    Args:
        input_file: Path to input Excel file
        department: Default department for incidents (optional)
    """
    try:
        df = pd.read_excel(input_file)
        print(f"Processing {len(df)} incidents...")
        
        if department:
            if department.lower() in VALID_DEPARTMENTS:
                print(f"Using department: {department}")
            else:
                print(f"Warning: '{department}' is not a valid department.")
                print(f"Valid departments: {', '.join(VALID_DEPARTMENTS)}")
                department = None

        results_df = process_incidents_rowwise(df, default_department=department)
        print(results_df)

        # Save results
        results_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(results_df.to_dict(orient='records'), f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to '{OUTPUT_CSV}' and '{OUTPUT_JSON}'.")
        
        # Print department statistics if available
        if 'department' in results_df.columns:
            print("\nDepartment Statistics:")
            dept_counts = results_df['department'].value_counts()
            for dept, count in dept_counts.items():
                print(f"  {dept}: {count} incident(s)")
                
    except FileNotFoundError:
        print(f"Error: The file at {input_file} was not found. Please check the path.")
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the safety event classifier prompt chain.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Valid departments:
  - internal medicine
  - surgery
  - ob/gyn/nicu
  - radiology/imaging
  - outpatient/ER

Examples:
  python safety_event_classifier.py -f incidents.xlsx
  python safety_event_classifier.py -f incidents.xlsx -d surgery
  python safety_event_classifier.py --file incidents.xlsx --department "internal medicine"
        """
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="file_path",
        default=DEFAULT_INPUT_FILE,
        help="Path to the input incident file (Excel format)",
    )
    parser.add_argument(
        "-d",
        "--department",
        metavar="department",
        default=None,
        help="Default department for incidents (e.g., 'surgery', 'internal medicine')",
    )
    
    args = parser.parse_args()

    main(args.file, args.department)