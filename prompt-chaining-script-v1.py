import pandas as pd
import requests
import re
import json

# --- Configuration ---
# Define Ollama API endpoint and model
OLLAMA_API_URL = "<__API URL__>" # Not necessary using Ollama URL in our project, but keeping this line defined for now as it is called in the last chunk
OLLAMA_MODEL = "llama3.2:latest" # IMPORTANT: Use exact model tag here!

FILE_PATH = r"<__File Containing Data for Classification__>"

# Map subcategories to main classes for final output, will not be needed if we are not classifying subcategories
# SUBCATEGORY_TO_BIG_CATEGORY = {
#     "NME1": "Near Miss", "NME2": "Near Miss", "NME3": "Near Miss",
#     "PSE1": "Precursor", "PSE2": "Precursor", "PSE3": "Precursor", "PSE4": "Precursor",
#     "SSE1": "Serious", "SSE2": "Serious", "SSE3": "Serious", "SSE4": "Serious", "SSE5": "Serious",
#     "NSE": "Not a Safety Event"
# }

############################################
# Below are prompt templates, without few-shot learning examples yet. Will be continuously updated/changed.
############################################

# --- Prompt Templates ---

# Prompt 1: Determine Deviation from GAPS
# This prompt's primary goal is to answer the first decision tree question: Was there a deviation from Generally Accepted Performance Standards (GAPS)?
PROMPT_TEMPLATE_GAPS_DEVIATION = """
You are a hospital safety officer. Analyze the following incident to determine if there was a **deviation from Generally Accepted Performance Standards (GAPS)** in healthcare.

Respond with ONLY one of the following words: "Yes" or "No". Do not provide any explanation, examples, or extra words.

--- Considerations ---
A deviation from GAPS is when a difference is detected between expected and actual performance. Consider the following when identifying deviations from GAPS:
- Nationally recognized best practices and standards of care in Canada
- Industry-imposed practice mandates and requirements
- Professional practice standards
- Organization's obligation to best protect the patient from harm

--- Examples ---


--- Classify the incident below ---
Incident: {incident}
Deviation from GAPS:
"""


# Prompt 2: (if GAPS deviation is "Yes")
# This answers "Did the deviation reach the patient?"
PROMPT_TEMPLATE_REACHED_PATIENT = """
You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred, determine if this **deviation reached the patient**. An incident is considered to have "reached the patient" when the patient is directly exposed to the harm or potential harm.

Respond with ONLY one of the following words: "Yes" or "No". Do not provide any explanation, examples, or extra words.

--- Examples ---


--- Classify the incident below ---
Incident: {incident}
Deviation reached patient:
"""


# Prompt 3: (if Deviation reached patient is "Yes")
# This answers "Did the deviation cause moderate to severe harm or death?"
PROMPT_TEMPLATE_HARM_LEVEL = """
You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred and reached the patient, determine if this **deviation caused moderate to severe harm or death**.

Respond with ONLY one of the following words: "Yes" or "No". Do not provide any explanation, examples, or extra words.

--- Examples ---

--- Classify the incident below ---
Incident: {incident}
Harm level:
"""


############################################
# PERHAPS BELOW NEEDS TO CHANGE TO SCRIPT REQUIREMENTS MATCHING WHAT'S TAUGHT IN AC215?
############################################


# --- LLM Interaction Function ---
def call_ollama_llm(prompt_text: str, max_tokens: int = 10) -> str:
    """
    Makes a streaming API call to the Ollama LLM and returns the concatenated response.
    Handles potential connection and JSON decoding errors.
    """
    raw_response_content = ""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt_text,
                "stream": True,
                "options": {
                    "temperature": 0,
                    "num_predict": max_tokens
                }
            },
            stream=True
        )

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        json_chunk = json.loads(line.decode('utf-8', errors='replace'))
                        if "response" in json_chunk:
                            raw_response_content += json_chunk["response"]
                        if json_chunk.get("done"):
                            break
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not decode JSON line from Ollama stream. Line: {line.decode('utf-8')[:100]}..., Error: {e}")
                        return "Stream JSON Decode Error"
            raw_response_content = raw_response_content.strip()
            raw_response_content = raw_response_content.replace('\u00A0', ' ')
            raw_response_content = raw_response_content.replace('\u2192', '')

            if not raw_response_content:
                print(f"Warning: Ollama returned an empty response.")
                return "No response generated by model."
        else:
            print(f"API Error (Status {response.status_code}): {response.text[:200]}...")
            return f"API Error (Status {response.status_code})"

    except requests.exceptions.ConnectionError:
        print("Connection Error: Ollama server not running or unreachable. Please start Ollama.")
        return "Connection Error"
    except Exception as e:
        print(f"An unexpected error occurred during API call: {e}")
        return "Unexpected API Error"

    return raw_response_content.strip().replace('.', '')



############################################
# CALL_OLLAMA_LLM USAGE IN BELOW CHUNK NEEDS TO BE UPDATED ACCORDING TO CHANGES MADE IN ABOVE CHUNK
############################################


# --- Processing Logic ---
def process_incidents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes incidents using a sequential prompt chaining approach with conditional branching.
    """
    
    results = []
    for i, row in df.iterrows():
        incident_description = row["Brief Factual Description"]

        # Initialize classification variables for this incident
        gaps_deviation_answer = "N/A"
        reached_patient_answer = "N/A"
        harm_level_answer = "N/A"
        final_classification_code = "Unknown"
        rationale_text = "N/A"

        # -----------------------------------------------------------
        # Step 1: Determine Deviation from GAPS
        # -----------------------------------------------------------

        # Format the prompt using the dynamically generated text
        gaps_deviation_prompt = PROMPT_TEMPLATE_GAPS_DEVIATION.format(incident=incident_description)
        gaps_deviation_answer = call_ollama_llm(gaps_deviation_prompt, max_tokens=5)

        if gaps_deviation_answer.upper() == "NO":
            # --- CLASSIFY AS NSE ---
            final_classification_code = "NSE"
            # final_top_level_category = SUBCATEGORY_TO_BIG_CATEGORY["NSE"]
            rationale_text = "Incident identified as having no deviation from Generally Accepted Performance Standards (GAPS)."
            print(f"Incident {i+1}: No GAPS deviation detected. Classified as NSE.")
        elif gaps_deviation_answer.upper() == "YES":
            print(f"Incident {i+1}: GAPS deviation detected. Proceeding to next step (Reached Patient).")
            # -----------------------------------------------------------
            # Step 2: Did the deviation reach the patient?
            # -----------------------------------------------------------
            reached_patient_prompt = PROMPT_TEMPLATE_REACHED_PATIENT.format(incident=incident_description)
            reached_patient_answer = call_ollama_llm(reached_patient_prompt, max_tokens=5)

            if reached_patient_answer.upper() == "NO":
                 # --- CLASSIFY AS NME (Near Miss Event) ---
                print(f"Incident {i+1}: Deviation did not reach patient. Classified as NME.")
                final_classification_code = "NME" 
                rationale_text = f"Deviation occurred but did not reach the patient. Classified as {nme_subcategory_output}."
                print(f"Incident {i+1}: Classified as {final_classification_code}.")
            elif reached_patient_answer.upper() == "YES":
                print(f"Incident {i+1}: Deviation reached patient. Proceeding to next step (Harm Level).")
                # -----------------------------------------------------------
                # Step 3: Did the deviation cause moderate to severe harm or death?
                # -----------------------------------------------------------
                harm_level_prompt = PROMPT_TEMPLATE_HARM_LEVEL.format(incident=incident_description)
                harm_level_answer = call_ollama_llm(harm_level_prompt, max_tokens=5)

                if harm_level_answer.upper() == "NO":
                     # --- CLASSIFY AS PSE (Precursor Safety Event) ---
                    print(f"Incident {i+1}: No moderate/severe harm. Classified as PSE.")
                    final_classification_code = "PSE" 
                    rationale_text = f"Deviation reached patient with no or minimal harm. Classified as {pse_subcategory_output}."
                    print(f"Incident {i+1}: Classified as {final_classification_code}.")
                elif harm_level_answer.upper() == "YES":
                    # --- CLASSIFY AS SSE (Serious Safety Event) ---
                    print(f"Incident {i+1}: Moderate/severe harm occurred. Classified as SSE.")
                    final_classification_code = "SSE" 
                    rationale_text = f"Deviation caused moderate/severe harm or death. Classified as {sse_subcategory_output}."
                    print(f"Incident {i+1}: Classified as {final_classification_code}.")
                else:
                    print(f"Incident {i+1}: Unexpected harm level answer: '{harm_level_answer}'")
                    rationale_text = f"Error: Unexpected harm level answer '{harm_level_answer}'."
            else:
                print(f"Incident {i+1}: Unexpected 'reached patient' answer: '{reached_patient_answer}'")
                rationale_text = f"Error: Unexpected 'reached patient' answer '{reached_patient_answer}'."
        else:
            print(f"Incident {i+1}: Unexpected GAPS deviation answer: '{gaps_deviation_answer}'")
            rationale_text = f"Error: Unexpected GAPS deviation answer '{gaps_deviation_answer}'."


        results.append({
            "incident": incident_description,
            "gaps_deviation_check": gaps_deviation_answer,
            "reached_patient_check": reached_patient_answer,
            "harm_level_check": harm_level_answer,
            "final_classification_code": final_classification_code,
            # "top_level_category": final_top_level_category,
            # "top_subcategory_1": final_top_subcategory_1,
            # "top_subcategory_2": final_top_subcategory_2, # Will remain "None" in this setup
            "rationale": rationale_text
        })
        pass
    return pd.DataFrame(results)


# --- Execution ---
if __name__ == "__main__":
    try:
        df = pd.read_excel(FILE_PATH)
        # df = pd.read_excel(FILE_PATH, sheet_name="")
        print("DataFrame loaded:")
        print(df.head())

        print("\n--- Starting Sequential Prompt Chaining on All Incidents ---")
        df_output = process_incidents(df) 

        print("\n--- Classification Results ---")
        print(df_output)

        # Save results
        df_output.to_csv("chaining_output.csv", index=False, encoding='utf-8')
        with open("chaining_output.json", "w", encoding="utf-8") as f:
            json.dump(df_output.to_dict(orient='records'), f, indent=2, ensure_ascii=False)

    except FileNotFoundError:
        print(f"Error: The file at {FILE_PATH} was not found. Please check the path.")
    except Exception as e:
        print(f"An error occurred during execution: {e}")


