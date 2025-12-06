"""
Data Pipeline - Synthetic Medical Incident Data Generation

Generates synthetic hospital safety incident data for LLM training and evaluation
using Google's Gemini model via Vertex AI.
"""

from google import genai
import pandas as pd
import re
import os
import argparse

# Configuration from environment variables with defaults
GCP_PROJECT = os.environ.get("GCP_PROJECT", "apcomp215-group88")
GCP_LOCATION = os.environ.get("GCP_REGION", "us-central1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash")

# Default output settings
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_OUTPUT_FILE = "generated_incidents.csv"


def init_client():
    """Initialize the Vertex AI GenAI client."""
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT,
        location=GCP_LOCATION
    )


def generate_data(llm_client, num_samples: int, output_file: str):
    """
    Generate synthetic medical incident data using LLM.
    
    Args:
        llm_client: The GenAI client
        num_samples: Number of incidents to generate
        output_file: Path to save the output file
    """
    prompt = f"""
        You are a medical safety analyst.

        There are different levels of medical safety incidents. Ranked by seriousness, they are serious safety events (SSE), precursor safety events (PSE), near miss safety events (NME), and no safety events (NSE).

        Please generate {num_samples} examples of medical safety incidents across different levels of safety events in different departments,
        including internal medicine, surgery, ob/gyn/nicu, radiology/imaging, and outpatient/ER.

        Each event description should be NO LESS THAN 60 words, detailed and realistic, either personal or based on real historical public cases. Need to describe what hospital did lead to the incidents and the reason behind the story.

        Do NOT label or classify them with severity levels (e.g., serious safety events (SSE)/precursor safety event (PSE)/ near miss safety event (NME)/ no safety event (NSE)).

        Focus on medically plausible situations reflecting real hospital or clinical settings.

        Format the output in a structured, numbered list like this:

        1. [Department Name]: [Detailed incident description...]
        2. [Department Name]: [Detailed incident description...]
        ...
        {num_samples}. [Department Name]: [Detailed incident description...]

        SSE Example:
        A patient was admitted to the critical care unit with congestive heart failure and later has a new complaint of chest pain persisting over several hours. Tylenol is administered but does not decrease the patient's pain scale rating. The Resident orders a laboratory work-up. An EKG shows that the patient is experiencing an acute ST-elevation myocardial infarction. The attending cardiologist is called, but does not respond to multiple pages. The nurse does not escalate the patient's emergent condition to other physicians or the rapid response team. The patient continues to decompensate, codes and expires.

        PSE Example:
        A patient was being treated in the Cardiac Progressive Care Unit and had a heparin lock in place. As part of the routine hep-lock care, the nurse administered what she thought was the usual hep-lock flush solution from an unlabeled syringe she previously placed at the bedside. However, the syringe actually contained Cardizem, which she administered to the patient. The patient experienced an immediate hypotensive reaction, which quickly resolved without further incident.

        NME Example:
        A nurse in a health care systems' float pool is assigned to work at the organization's Assisted Living Facility for several days. He begins passing out medications to the residents and some of them aren't in their room but in the facility's Day Room. Most of the resident's don't wear arm bands but have pictures inside their rooms for identification. The nurse depended on patient's selfidentifying when passing meds in the Day Room. He had been introduced to the patients earlier that day and thinking he knew the patients, did the identification with saying the patient's name as it seemed quicker and he was behind in this task. When the patient agreed, he gave the pill packet to them. Another resident hearing what transpired walked up to tell the nurse that this patient was responding to the wrong name. The nurse took the medications back and began to perform the identification process correctly by asking the patient to state name and DOB.

        NSE Example:
        A healthy Gravida 2 Para1 40-week gestation mother presents in active labor requiring routine monitoring according to Labor & Delivery protocols. Labor progresses to delivery of a healthy 6-pound infant with Apgar scores of 10 and 10. Within 2 minutes post-delivery, the mother, who is still being monitored, begins to develop extreme respiratory distress and signs of disseminated intravascular clotting (DIC) syndrome. Despite all emergent efforts to reverse the situation, the mother succumbs to what is later diagnosed as an amniotic fluid embolism.

        Do NOT provide any explanation, examples, or extra words. Just provide the numbered list as specified.
    """

    print(f"Generating {num_samples} synthetic medical incidents...")
    print(f"Using model: {LLM_MODEL}")
    print(f"GCP Project: {GCP_PROJECT}")
    print(f"GCP Region: {GCP_LOCATION}")
    print()

    response = llm_client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )
    paragraph = response.text
    print("Generation complete!")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save raw response
    raw_output = os.path.join(output_dir if output_dir else DEFAULT_OUTPUT_DIR, "raw_response.txt")
    os.makedirs(os.path.dirname(raw_output) if os.path.dirname(raw_output) else DEFAULT_OUTPUT_DIR, exist_ok=True)
    with open(raw_output, "w", encoding="utf-8") as f:
        f.write(paragraph)
    print(f"Raw response saved to: {raw_output}")

    # Parse response into structured data
    pattern = re.compile(r"\d+\.\s*(.+?):\s*(.+?)(?=\n\d+\.|\Z)", re.DOTALL)
    matches = pattern.findall(paragraph)
    
    if matches:
        df = pd.DataFrame([
            {
                # Remove markdown bold markers (**) from department and description
                "Department": re.sub(r'\*+', '', department).strip(),
                "Incident Description": re.sub(r'\*+', '', description).strip(),
            }
            for department, description in matches
        ])
        print(f"Successfully parsed {len(df)} incidents")
    else:
        print("Warning: Could not parse structured data, saving raw response")
        df = pd.DataFrame([{"Raw Response": paragraph.strip()}])

    # Save to appropriate format based on file extension
    if output_file.endswith('.xlsx'):
        df.to_excel(output_file, index=False)
    else:
        df.to_csv(output_file, index=False)
    
    print(f"Data saved to: {output_file}")
    print()
    print(f"Generated {len(df)} incidents successfully!")
    
    return df


def main():
    """Main entry point for data generation."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic medical incident data for training and evaluation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data_generation.py --num_samples 10
  python data_generation.py --num_samples 50 --output_file outputs/large_dataset.csv
  python data_generation.py --num_samples 100 --output_file outputs/dataset.xlsx
        """
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=10,
        help="Number of incident examples to generate (default: 10)",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default=os.path.join(DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE),
        help=f"Output file path (default: {DEFAULT_OUTPUT_DIR}/{DEFAULT_OUTPUT_FILE})",
    )

    args = parser.parse_args()
    
    # Initialize client and generate data
    llm_client = init_client()
    generate_data(llm_client, args.num_samples, args.output_file)


if __name__ == "__main__":
    main()
