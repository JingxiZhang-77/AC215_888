"""
Simplified prompt utilities for the Safety Event Classification Frontend
More robust error handling and simpler prompts for web interface
"""

import os
from google import genai

# GCP configuration
GCP_PROJECT = "apcomp215-group88"
GCP_LOCATION = "us-central1"
GENERATIVE_MODEL = "gemini-2.5-flash"

# Initialize the LLM Client
llm_client = genai.Client(
    vertexai=True, project=GCP_PROJECT, location=GCP_LOCATION
)

def _call_llm_with_retry(prompt: str, max_retries: int = 3) -> str:
    """
    Call LLM with retry logic and return text response
    """
    for attempt in range(max_retries):
        try:
            response = llm_client.models.generate_content(
                model=GENERATIVE_MODEL,
                contents=prompt,
            )
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            
            if hasattr(response, 'candidates') and response.candidates:
                first_candidate = response.candidates[0]
                if hasattr(first_candidate, 'content') and hasattr(first_candidate.content, 'parts'):
                    parts = first_candidate.content.parts
                    if parts:
                        text = ''.join(part.text for part in parts if hasattr(part, 'text'))
                        if text:
                            return text.strip()
            
            raise ValueError("No valid response text found")
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
            continue
    
    raise Exception("Failed to get response from LLM")

def _parse_yes_no_response(response_text: str) -> bool:
    """
    Parse a Yes/No response from LLM
    Returns True for Yes, False for No
    """
    response_lower = response_text.lower().strip()
    
    # Look for explicit yes/no
    if 'yes' in response_lower[:50]:  # Check first 50 chars
        return True
    if 'no' in response_lower[:50]:
        return False
    
    # Look for true/false
    if 'true' in response_lower[:50]:
        return True
    if 'false' in response_lower[:50]:
        return False
    
    # Default to False if unclear (safer for safety events)
    print(f"Warning: Unclear response, defaulting to False: {response_text[:100]}")
    return False

def prompt1_single_incident(incident_text: str) -> bool:
    """
    Step 1: Determine if there was a deviation from Generally Accepted Performance Standards (GAPS)
    Returns: True if deviation detected, False otherwise
    """
    prompt = f"""You are a hospital safety officer analyzing incidents.

Question: Was there a deviation from Generally Accepted Performance Standards (GAPS) in this incident?

A deviation from GAPS means a difference between expected and actual performance, considering:
- Nationally recognized best practices and standards of care
- Industry-imposed practice mandates and requirements
- Professional practice standards
- Organization's obligation to protect patients from harm

Incident Description:
{incident_text}

Answer with ONLY "Yes" or "No" as the first word of your response, followed by a brief explanation.

Answer:"""
    
    try:
        response = _call_llm_with_retry(prompt)
        result = _parse_yes_no_response(response)
        print(f"Prompt 1 - GAPS Deviation: {result} (Response: {response[:100]}...)")
        return result
    except Exception as e:
        print(f"Error in prompt1: {e}")
        raise

def prompt2_single_incident(incident_text: str) -> bool:
    """
    Step 2: Determine if the deviation reached the patient
    Returns: True if it reached patient, False otherwise
    """
    prompt = f"""You are a hospital safety officer analyzing incidents.

Question: Did the deviation/error reach the patient?

This means the error actually affected or could have affected the patient directly, not just internal processes.

Incident Description:
{incident_text}

Answer with ONLY "Yes" or "No" as the first word of your response, followed by a brief explanation.

Answer:"""
    
    try:
        response = _call_llm_with_retry(prompt)
        result = _parse_yes_no_response(response)
        print(f"Prompt 2 - Reached Patient: {result} (Response: {response[:100]}...)")
        return result
    except Exception as e:
        print(f"Error in prompt2: {e}")
        raise

def prompt3_single_incident(incident_text: str) -> bool:
    """
    Step 3: Determine if the incident caused moderate/severe harm or death
    Returns: True if significant harm occurred, False for no/minimal harm
    """
    prompt = f"""You are a hospital safety officer analyzing incidents.

Question: Did this incident cause moderate harm, severe harm, or death to the patient?

Consider:
- Moderate harm: Temporary injury requiring intervention (e.g., additional treatment, longer hospital stay)
- Severe harm: Permanent injury or significant temporary harm
- Death: Patient died as a result of the incident

NO or MINIMAL harm means: No injury, or minor temporary discomfort that resolved quickly without intervention.

Incident Description:
{incident_text}

Answer with ONLY "Yes" (for moderate/severe harm or death) or "No" (for no/minimal harm) as the first word of your response, followed by a brief explanation.

Answer:"""
    
    try:
        response = _call_llm_with_retry(prompt)
        result = _parse_yes_no_response(response)
        print(f"Prompt 3 - Significant Harm: {result} (Response: {response[:100]}...)")
        return result
    except Exception as e:
        print(f"Error in prompt3: {e}")
        raise
