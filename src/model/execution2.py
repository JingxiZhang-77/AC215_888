import pandas as pd
import json
from prompt_chaining import (
    prompt1_single_incident,
    prompt2_single_incident,
    prompt3_single_incident
)

FILE_PATH = "incident_data.xlsx"  # update this path as needed
OUTPUT_CSV = "chaining_output.csv"
OUTPUT_JSON = "chaining_output.json"

def process_incidents_rowwise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process incidents in DataFrame one-by-one, running prompt chain with per-incident branching.
    """
    results = []
    for i, row in df.iterrows():
        incident_description = row["Brief Factual Description"]

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
            "gaps_deviation_check": gaps_deviation_ans,
            "reached_patient_check": reached_patient_ans,
            "harm_level_check": harm_level_ans,
            "final_classification_code": final_classification,
            "rationale": rationale_text
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    try:
        df = pd.read_excel(FILE_PATH)
        print(f"Processing {len(df)} incidents...")

        results_df = process_incidents_rowwise(df)
        print(results_df)

        # Save results
        results_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(results_df.to_dict(orient='records'), f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to '{OUTPUT_CSV}' and '{OUTPUT_JSON}'.")
    except FileNotFoundError:
        print(f"Error: The file at {FILE_PATH} was not found. Please check the path.")
    except Exception as e:
        print(f"An error occurred during execution: {e}")