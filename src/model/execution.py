import pandas as pd
import json
from prompt_chaining import read_incidents, prompt1, prompt2, prompt3

FILE_PATH = "<incident_data_file>"  # Update as needed
LIMIT = None  # Optionally set a limit on number of incidents

# Define output codes for clarity
NSE = "NSE"
NME = "NME"
PSE = "PSE"
SSE = "SSE"

def classify_events(file_path, limit=None):
    # Load all incidents as a list of strings
    incidents = read_incidents(file_path, limit)
    n = len(incidents)

    # Run prompt1 for all incidents
    gaps_deviation_answers = prompt1(file_path, limit)
    
    # Only run prompt2 for those with a GAPS deviation (True)
    reached_patient_answers = [None] * n
    harm_level_answers = [None] * n
    final_classification_codes = [None] * n
    rationales = [None] * n
    
    # For batch efficiency, run prompt2/prompt3 on all when possible, then map back
    prompt2_candidates = [idx for idx, val in enumerate(gaps_deviation_answers) if val]
    prompt2_indices = []
    prompt2_incidents = []
    for idx in prompt2_candidates:
        prompt2_indices.append(idx)
        prompt2_incidents.append(incidents[idx])
    
    # Prepare a file or use a modded version to process only these? 
    # Instead, easiest is run prompt2 again on whole file, mapping only those we want.
    all_reached_patient = prompt2(file_path, limit)
    
    prompt3_candidates = []
    for idx in prompt2_candidates:
        _reached = all_reached_patient[idx]
        reached_patient_answers[idx] = _reached
        if not _reached:
            final_classification_codes[idx] = NME
            rationales[idx] = "Deviation occurred but did not reach the patient."
        else:
            prompt3_candidates.append(idx)
    
    # Prompt3: Only those where deviation reached the patient
    all_harm_levels = prompt3(file_path, limit)
    for idx in prompt3_candidates:
        _harm = all_harm_levels[idx]
        harm_level_answers[idx] = _harm
        if _harm:
            final_classification_codes[idx] = SSE
            rationales[idx] = "Deviation reached the patient and caused moderate/severe harm or death."
        else:
            final_classification_codes[idx] = PSE
            rationales[idx] = "Deviation reached the patient with no or minimal harm."
    
    # For those with no GAPS deviation
    for idx, has_gaps in enumerate(gaps_deviation_answers):
        if not has_gaps:
            final_classification_codes[idx] = NSE
            rationales[idx] = "No deviation from Generally Accepted Performance Standards (GAPS)."

    # Compose DataFrame
    df = pd.DataFrame({
        "incident": incidents,
        "gaps_deviation_check": ['Yes' if x else 'No' for x in gaps_deviation_answers],
        "reached_patient_check": [
            'Yes' if x else ('No' if x is not None else 'N/A') for x in reached_patient_answers
        ],
        "harm_level_check": [
            'Yes' if x else ('No' if x is not None else 'N/A') for x in harm_level_answers
        ],
        "final_classification_code": final_classification_codes,
        "rationale": rationales,
    })
    return df

if __name__ == "__main__":
    df_output = classify_events(FILE_PATH, LIMIT)
    print(df_output)
    df_output.to_csv("chaining_output.csv", index=False, encoding='utf-8')
    with open("chaining_output.json", "w", encoding="utf-8") as f:
        json.dump(df_output.to_dict(orient='records'), f, indent=2, ensure_ascii=False)