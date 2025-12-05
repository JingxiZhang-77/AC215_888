from google import genai
import pandas as pd
import re
import os
import argparse

GCP_PROJECT = "apcomp215-group88"
GCP_LOCATION = "us-central1"
LLM_MODEL = "gemini-2.5-flash"

#############################################################################
#                       Initialize the LLM Client                           #
llm_client = genai.Client(
    vertexai=True, project=GCP_PROJECT, location=GCP_LOCATION)
#############################################################################

def generate_data(input_prompt):

    print("Start generating data...")
    response = llm_client.models.generate_content(
        model=LLM_MODEL, contents=input_prompt
    )
    paragraph = response.text
    print("Generated finished")

    # Save raw response to txt file
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/raw_response.txt", "w", encoding="utf-8") as f:
        f.write(paragraph)
    print("Raw response saved to outputs/raw_response.txt")

    pattern = re.compile(r"\d+\.\s*(.+?):\s*(.+?)(?=\n\d+\.|\Z)", re.DOTALL)
    matches = pattern.findall(paragraph)
    if matches:
        df = pd.DataFrame(
            [
                {
                    "Department": department.strip(),
                    "Incident Description": description.strip(),
                }
                for department, description in matches
            ]
        )
    else:
        df = pd.DataFrame([{"Raw Response": paragraph.strip()}])
    os.makedirs("outputs", exist_ok=True)
    df.to_excel("outputs/medical_incidents.xlsx", index=False)
    print("Sucessfully store the data at outputs folder")

def main(args):

    print(f"Now the program will generate {args} data")

    prompt = f"""
        You are a medical safety analyst.

        There are different levels of medical safety incidents. Ranked by seriousness, they are serious safety events (SSE), precursor safety events (PSE), near miss safety events (NME), and no safety events (NSE).

        Please generate {args} examples of medical safety incidents across different levels of safety events in different departments,
        including internal medicine, surgery, ob/gyn/nicu, radiology/imaging, and outpatient/ER.

        Each event description should be NO LESS THAN 60 words, detailed and realistic, either personal or based on real historical public cases. Need to describe what hospital did lead to the incidents and the reason behind the story.

        Do NOT label or classify them with severity levels (e.g., serious safety events (SSE)/precursor safety event (PSE)/ near miss safety event (NME)/ no safety event (NSE)).

        Focus on medically plausible situations reflecting real hospital or clinical settings.

        Format the output in a structured, numbered list like this:

        1. [Department Name]: [Detailed incident description...]
        2. [Department Name]: [Detailed incident description...]
        ...
        {args}. [Department Name]: [Detailed incident description...]

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
    
    generate_data(prompt)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Generate medical incident examples.")
    parser.add_argument(
        "--num_generate",
        type=int,
        default=5,
        help="Number of incident examples to generate (default: 5)",
    )

    args = parser.parse_args()
    main(args.num_generate)