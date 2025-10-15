"""
Module that implements the three prompts which are chained together with conditional branching based on the answers.
"""

import os
import io
import argparse
import shutil
import glob
import sys
from google import genai
from google.genai import types
from google.genai.types import Content, Part, GenerationConfig, ToolConfig
from google.genai import errors
import time

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

# Prompt 1: Determine Deviation from GAPS
def prompt1(file_path):
    """
    Render the GAPS-deviation classification prompt for a single incident.

    Args:
        file_path: Path to the text file containing the incident description.
    """

    # Validate file_path
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError("File not found: {}".format(file_path))

    # Read the incident text from the file
    with open(file_path, "r", encoding="utf-8") as f:
        incident_text = f.read().strip()

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

    # Render the prompt with the incident text
    rendered_prompt = PROMPT_TEMPLATE_GAPS_DEVIATION.format(incident=incident_text)

    # Generate the response from the LLM
    response = llm_client.models.generate_content(
        model=GENERATIVE_MODEL,
        contents=rendered_prompt,
    )
    candidate_text = getattr(response, "text", "")
    if not candidate_text and getattr(response, "candidates", None):
        candidate_text = "".join(
            getattr(part, "text", "") for part in response.candidates[0].content.parts
        )
    candidate_text = candidate_text.strip().lower()
    if candidate_text == "yes":
        # For test purposes, print the response
        print("Prompt 1 Response: Yes")
        return True
    if candidate_text == "no":
        # For test purposes, print the response
        print("Prompt 1 Response: No")
        return False
    raise ValueError(f"Unexpected LLM response: {candidate_text or 'empty'}")

# Prompt 2: (if GAPS deviation is "Yes")
# This answers "Did the deviation reach the patient?"
def prompt2(file_path):
    """
    Render the prompt for determining if the deviation reached the patient.

    Args:
        file_path: Path to the text file containing the incident description.
    """

    # Validate file_path
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError("File not found: {}".format(file_path))

    # Read the incident text from the file
    with open(file_path, "r", encoding="utf-8") as f:
        incident_text = f.read().strip()

    PROMPT_TEMPLATE_DEVIATION_REACHED = """
        You are a hospital safety officer. Given that a deviation from Generally Accepted Performance Standards (GAPS) occurred, determine if this **deviation reached the patient**. An incident is considered to have "reached the patient" when the patient is directly exposed to the harm or potential harm.

        Respond with ONLY one of the following words: "Yes" or "No". Do NOT provide any explanation, examples, or extra words.

        --- Classify the incident below ---
        Incident: {incident}
        Deviation reached patient:
    """.strip().strip("\n")

    # Render the prompt with the incident text
    rendered_prompt = PROMPT_TEMPLATE_DEVIATION_REACHED.format(incident=incident_text)

    # Generate the response from the LLM
    response = llm_client.models.generate_content(
        model=GENERATIVE_MODEL,
        contents=rendered_prompt,
    )
    candidate_text = getattr(response, "text", "")
    if not candidate_text and getattr(response, "candidates", None):
        candidate_text = "".join(
            getattr(part, "text", "") for part in response.candidates[0].content.parts
        )
    candidate_text = candidate_text.strip().lower()
    if candidate_text == "yes":
        # For test purposes, print the response
        print("Prompt 2 Response: Yes")
        return True
    if candidate_text == "no":
        # For test purposes, print the response
        print("Prompt 2 Response: No")
        return False
    raise ValueError(f"Unexpected LLM response: {candidate_text or 'empty'}")

# Prompt 3: (if Deviation reached patient is "Yes")
# This answers "Did the deviation cause moderate to severe harm or death?"
def prompt3(file_path):
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
    with open(file_path, "r", encoding="utf-8") as f:
        incident_text = f.read().strip()

    rendered_prompt = PROMPT_TEMPLATE_HARM_LEVEL.format(incident=incident_text)

    # Generate the response from the LLM
    response = llm_client.models.generate_content(
        model=GENERATIVE_MODEL,
        contents=rendered_prompt,
    )
    candidate_text = getattr(response, "text", "")
    if not candidate_text and getattr(response, "candidates", None):
        candidate_text = "".join(
            getattr(part, "text", "") for part in response.candidates[0].content.parts
        )
    candidate_text = candidate_text.strip().lower()
    if candidate_text == "yes":
        # For test purposes, print the response
        print("Prompt 3 Response: Yes")
        return True
    if candidate_text == "no":
        # For test purposes, print the response
        print("Prompt 3 Response: No")
        return False
    raise ValueError(f"Unexpected LLM response: {candidate_text or 'empty'}")


def main(args=None):
    print("Args:", args)

    if args.prompt1:
        if not args.file:
            print("error: -f/--file is required when using -prompt1", file=sys.stderr)
            return
        try:
            prompt1(args.file)
        except Exception as e:
            print("error: failed to render prompt1: {}".format(e), file=sys.stderr)
            return
        
    if args.prompt2:
        if not args.file:
            print("error: -f/--file is required when using -prompt2", file=sys.stderr)
            return
        try:
            prompt2(args.file)
        except Exception as e:
            print("error: failed to render prompt2: {}".format(e), file=sys.stderr)
            return
        
    if args.prompt3:
        if not args.file:
            print("error: -f/--file is required when using -prompt3", file=sys.stderr)
            return
        try:
            prompt3(args.file)
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
        help="Path to the input text file",
    )

    args = parser.parse_args()

    main(args)