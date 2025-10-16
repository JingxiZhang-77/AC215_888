"""
Module that implements the three prompts for classifying safety events using a
chain of responsibility pattern. Each prompt is encapsulated in its own function,
allowing for modular testing and potential reuse in different contexts.
"""

import argparse
import builtins
import csv
import glob
import os
import shutil
import sys
import time

from google import genai
from google.genai import errors, types
from google.genai.types import Content, GenerationConfig, Part, ToolConfig

try:
    import openpyxl  # type: ignore
except ImportError:
    openpyxl = None

# GCP configuration
GCP_PROJECT = "apcomp215-group88"
BUCKET_NAME = "group88-bucket-1"
GCP_LOCATION = "us-central1"
GENERATIVE_MODEL = "gemini-2.5-flash"

#############################################################################
#                       Initialize the LLM Client                           #
llm_client = genai.Client(
    vertexai=True, project=GCP_PROJECT, location=GCP_LOCATION)
#############################################################################

def read_incidents(file_path, limit=None):
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if limit is None:
        max_incidents = float("inf")
    else:
        if limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        max_incidents = limit
    ext = os.path.splitext(file_path)[1].lower()
    incidents = []

    def should_stop():
        return len(incidents) >= max_incidents

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                text = line.strip()
                if text:
                    incidents.append(text)
                    if should_stop():
                        break
    elif ext == ".csv":
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                row_text = " ".join(value for value in (cell.strip() for cell in row) if value)
                if row_text:
                    incidents.append(row_text)
                    if should_stop():
                        break
    elif ext == ".xlsx":
        if openpyxl is None:
            raise ImportError("openpyxl is required to read .xlsx files.")
        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        try:
            worksheet = workbook.active
            for row in worksheet.iter_rows(values_only=True):
                row_values = [str(cell).strip() for cell in row if cell not in (None, "")]
                if row_values:
                    incidents.append(" ".join(row_values))
                    if should_stop():
                        break
        finally:
            workbook.close()
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    if not incidents:
        raise ValueError(f"No incident data found in {file_path}.")
    return incidents

def generate_yes_no_response(contents):
    response = llm_client.models.generate_content(
        model=GENERATIVE_MODEL,
        contents=contents,
    )
    candidate_text = getattr(response, "text", "")
    if not candidate_text and getattr(response, "candidates", None):
        candidate_text = "".join(
            getattr(part, "text", "") for part in response.candidates[0].content.parts
        )
    normalized = candidate_text.strip().lower()
    if normalized not in {"yes", "no"}:
        raise ValueError(f"Unexpected LLM response: {candidate_text or 'empty'}")
    return normalized

# Prompt 1: Determine Deviation from GAPS
def prompt1(file_path, limit=None, print=True):
    """
    Render the GAPS-deviation classification prompt for each incident in the file.

    Args:
        file_path: Path to the text file containing the incident description.
    """

    # TODO(Bruce): Should we add an example prompt here to guide the LLM?
    PROMPT_TEMPLATE_GAPS_DEVIATION = """
        You are a hospital safety officer. Analyze the following incident to determine if there was a **deviation from Generally Accepted Performance Standards (GAPS)** in healthcare.

        Respond with ONLY one of the following words: "Yes" or "No". Do NOT provide any explanation, examples, or extra words.

        --- Considerations ---
        A deviation from GAPS is when a difference is detected between expected and actual performance. Consider the following when identifying deviations from GAPS:
        - Nationally recognized best practices and standards of care in Canada
        - Industry-imposed practice mandates and requirements
        - Professional practice standards
        - Organization's obligation to best protect the patient from harm

        --- Classify the incident below ---
        Incident: {incident}
        Deviation from GAPS:
    """.strip().strip("\n")

    # Validate file_path
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError("File not found: {}".format(file_path))

    # Read the incident text from the file
    incidents = read_incidents(file_path, limit)
    results = []
    for idx, incident_text in enumerate(incidents, start=1):
        rendered_prompt = PROMPT_TEMPLATE_GAPS_DEVIATION.format(incident=incident_text)

        # Generate the response from the LLM
        normalized = generate_yes_no_response(rendered_prompt)
        outcome = normalized == "yes"
        if print:
            builtins.print(f"Incident report {idx}: {'Deviation from GAPS occurred' if outcome else 'No deviation from GAPS occurred'}")
        results.append(outcome)
    return results

# Prompt 2: (if GAPS deviation is "Yes")
# This answers "Did the deviation reach the patient?"
def prompt2(file_path, limit=None, print=True):
    """
    Render the prompt for determining if the deviation reached the patient.

    Args:
        file_path: Path to the text file containing the incident description.
    """

    PROMPT_TEMPLATE_DEVIATION_REACHED = """
    You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred, determine if this **deviation reached the patient**. An incident is considered to have "reached the patient" when the patient is directly exposed to the harm or potential harm.

    Respond with ONLY one of the following words: "Yes" or "No". Do NOT provide any explanation, examples, or extra words.

    --- Classify the incident below ---
    Incident: {incident}
    Deviation reached patient:
""".strip().strip("\n")
    
    # Validate file_path
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError("File not found: {}".format(file_path))

    # Read the incident text from the file
    incidents = read_incidents(file_path, limit)
    results = []
    for idx, incident_text in enumerate(incidents, start=1):
        rendered_prompt = PROMPT_TEMPLATE_DEVIATION_REACHED.format(incident=incident_text)

        # Generate the response from the LLM
        normalized = generate_yes_no_response(rendered_prompt)
        outcome = normalized == "yes"
        if print:
            builtins.print(f"Incident report {idx}: {'Deviation reached the patient' if outcome else 'Deviation did not reach the patient'}")
        results.append(outcome)
    return results

# Prompt 3: (if Deviation reached patient is "Yes")
# This answers "Did the deviation cause moderate to severe harm or death?"
def prompt3(file_path, limit=None, print=True):
    """
    Render the prompt for determining if the deviation caused moderate to severe harm or death.

    Args:
        file_path: Path to the text file containing the incident description.
    """

    PROMPT_TEMPLATE_HARM_LEVEL = """
        You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred and reached the patient, determine if this **deviation caused moderate to severe harm or death**.

        Respond with ONLY one of the following words: "Yes" or "No". Do not provide any explanation, examples, or extra words.

        --- Classify the incident below ---
        Incident: {incident}
        Moderate to severe harm or death caused?:
    """.strip().strip("\n")

    # Validate file_path
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError("File not found: {}".format(file_path))

    # Read the incident text from the file
    incidents = read_incidents(file_path, limit)
    results = []
    for idx, incident_text in enumerate(incidents, start=1):
        rendered_prompt = PROMPT_TEMPLATE_HARM_LEVEL.format(incident=incident_text)

        # Generate the response from the LLM
        normalized = generate_yes_no_response(rendered_prompt)
        outcome = normalized == "yes"
        if print:
            builtins.print(f"Incident report {idx}: {'Deviation caused moderate to severe harm or death' if outcome else 'Deviation did not cause harm or death'}")
        results.append(outcome)
    return results


def prompt1_single_incident(incident_text: str) -> bool:
    PROMPT_TEMPLATE_GAPS_DEVIATION = """
    You are a hospital safety officer. Analyze the following incident to determine if there was a **deviation from Generally Accepted Performance Standards (GAPS)** in healthcare.

    Respond with ONLY one of the following words: "Yes" or "No". Do NOT provide any explanation, examples, or extra words.

    --- Considerations ---
    A deviation from GAPS is when a difference is detected between expected and actual performance. Consider the following when identifying deviations from GAPS:
    - Nationally recognized best practices and standards of care in Canada
    - Industry-imposed practice mandates and requirements
    - Professional practice standards
    - Organization's obligation to best protect the patient from harm

    --- Classify the incident below ---
    Incident: {incident}
    Deviation from GAPS:
    """
    rendered_prompt = PROMPT_TEMPLATE_GAPS_DEVIATION.format(incident=incident_text)
    normalized = generate_yes_no_response(rendered_prompt)
    return normalized == "yes"

def prompt2_single_incident(incident_text: str) -> bool:
    PROMPT_TEMPLATE_DEVIATION_REACHED = """
    You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred, determine if this **deviation reached the patient**. An incident is considered to have "reached the patient" when the patient is directly exposed to the harm or potential harm.

    Respond with ONLY one of the following words: "Yes" or "No". Do NOT provide any explanation, examples, or extra words.

    --- Classify the incident below ---
    Incident: {incident}
    Deviation reached patient:
    """
    rendered_prompt = PROMPT_TEMPLATE_DEVIATION_REACHED.format(incident=incident_text)
    normalized = generate_yes_no_response(rendered_prompt)
    return normalized == "yes"

def prompt3_single_incident(incident_text: str) -> bool:
    PROMPT_TEMPLATE_HARM_LEVEL = """
        You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred and reached the patient, determine if this **deviation caused moderate to severe harm or death**.

        Respond with ONLY one of the following words: "Yes" or "No". Do not provide any explanation, examples, or extra words.

        --- Classify the incident below ---
        Incident: {incident}
        Moderate to severe harm or death caused?:
    """
    rendered_prompt = PROMPT_TEMPLATE_HARM_LEVEL.format(incident=incident_text)
    normalized = generate_yes_no_response(rendered_prompt)
    return normalized == "yes"


def main(args=None):
    print("Args:", args)

    if args.prompt1:
        if not args.file:
            print("error: -f/--file is required when using -prompt1", file=sys.stderr)
            return
        try:
            prompt1(args.file, args.limit)
        except Exception as e:
            print("error: failed to render prompt1: {}".format(e), file=sys.stderr)
            return
        
    if args.prompt2:
        if not args.file:
            print("error: -f/--file is required when using -prompt2", file=sys.stderr)
            return
        try:
            prompt2(args.file, args.limit)
        except Exception as e:
            print("error: failed to render prompt2: {}".format(e), file=sys.stderr)
            return
        
    if args.prompt3:
        if not args.file:
            print("error: -f/--file is required when using -prompt3", file=sys.stderr)
            return
        try:
            prompt3(args.file, args.limit)
        except Exception as e:
            print("error: failed to render prompt3: {}".format(e), file=sys.stderr)
            return


if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="Render LLM prompts")

    parser.add_argument(
        "-p1",
        "--prompt1",
        action="store_true",
        help="Render Prompt 1: Determine Deviation from GAPS",
    )

    parser.add_argument(
        "-p2",
        "--prompt2",
        action="store_true",
        help="Render Prompt 2: Determine if Deviation Reached Patient",
    )

    parser.add_argument(
        "-p3",
        "--prompt3",
        action="store_true",
        help="Render Prompt 3: Determine if Deviation Caused Harm",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        metavar="file_path",
        help="Path to the input incident file (txt, csv, xlsx)",
    )

    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=None,
        metavar="number_of_rows",
        help="Number of incident rows to read from the file (defaults to all rows)",
    )

    args = parser.parse_args()

    main(args)
