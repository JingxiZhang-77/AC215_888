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

    with open(file_path, "r", encoding="utf-8") as f:
        incident_text = f.read().strip()

    # TODO(Bruce): Should we add an example prompt here to guide the LLM?
    PROMPT_TEMPLATE_GAPS_DEVIATION = """
        You are a hospital safety officer. Analyze the following incident to determine if there was a **deviation from Generally Accepted Performance Standards (GAPS)** in healthcare.

        Respond with ONLY one of the following words: "Yes" or "No". Do not provide any explanation, examples, or extra words.

        --- Considerations ---
        A deviation from GAPS is when a difference is detected between expected and actual performance. Consider the following when identifying deviations from GAPS:
        - Nationally recognized best practices and standards of care in Canada
        - Industry-imposed practice mandates and requirements
        - Professional practice standards
        - Organization's obligation to best protect the patient from harm

        --- Classify the incident below ---
        Incident: {incident}
        Deviation from GAPS:
    """.strip("\n")

    # Render the prompt with the incident text
    rendered_prompt = PROMPT_TEMPLATE_GAPS_DEVIATION.format(incident=incident_text)

    # Generate the response from the LLM
    response = llm_client.responses.generate(
        model=GENERATIVE_MODEL,
        contents=[Content(role="user", parts=[Part.from_text(rendered_prompt)])],
        config=GenerationConfig(temperature=0.0, max_output_tokens=5),
    )
    candidate_text = ""
    if response.candidates and getattr(response.candidates[0], "content", None):
        candidate_text = "".join(
            getattr(part, "text", "") for part in response.candidates[0].content.parts
        ).strip().lower()
    if candidate_text == "yes":
        return True
    if candidate_text == "no":
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
        "-f",
        "--file",
        help="Path to the input text file",
    )

    args = parser.parse_args()

    main(args)