# AC215 - Milestone2 
## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang
## Group Name
AC215_888
## Project
Design and build a web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI methodology.


## Data Generation
The dataset contains 100 detailed examples of medical safety incidents and 100 Gemini simulate data. Each entry represents a realistic clinical incident across various hospital departments, including:
- Internal Medicine
- Surgery
- OB/GYN & NICU
- Radiology / Imaging
- Outpatient / Emergency (ER)

The dataset is designed to simulate real-world hospital safety events.
After generation, each case is manually reviewed and labeled into one of four safety event levels:
- SSE (Serious Safety Event)
- PSE (Precursor Safety Event)
- NME (Near Miss Event)
- NSE (No Safety Event)

These labeled data are then used to fine-tune LLMs, enabling hospitals to better identify, classify, and prevent safety incidents — ultimately helping healthcare systems reduce medical errors and improve patient outcomes.

#### Prerequisites:

Before running the program, make sure you have:

- Docker Desktop installed and running

- A valid Google service account key (e.g. llm-service-account.json)

- Your own local copy of the source code(src/datapipline)

#### Step 1. Build the Docker Image

Run this command from the folder containing your `Dockerfile`:

```bash
docker build -t project_data -f Dockerfile .
```

#### Step 2. Run the Docker Container
You need to mount two folders into the container:
- Project folder → contains your Python code
- Secrets folder → contains your credentials (e.g., llm-service-account.json)

```bash
docker run --rm -ti `
  -v "YourPath\project_folder:/app" `
  -v "YourPath\secrets_folder:/app/secrets" `
  project
```

#### Step 3. Run the Python Script
Inside the container, run:
```bash
python data_generation.py
```
This will use Genimi to generate medical incidents data


## RAG Implementation

Our next step is to integrate RAG component into Prompt 1. This enhancement will allow the model to retrieve relevant mock hospital policies, clinical guidelines, and best-practice standards before generating its final classification.

## Model Classification

In the terminal, navigate to the project root and build the image:
```bash
docker build -t med-severity .
```
This will:
1. Install Python 3.11 + system dependencies  
2. Create a non-root user (`app`)  
3. Copy project files into `/src`  
4. Install dependencies via `uv sync`

And then, we can run the the Pipeline:
```bash
docker run -it med-severity
```

You’ll see:
```
Enter a medical safety incident description (or press Enter to use sample_input.txt):
```

- Type or paste your description and press Enter  
  → Example:  
  ```
  A nurse administered the wrong antibiotic but corrected the dose immediately.
  ```

**Output Example:**
```
Classification: SSE – Minor temporary harm
Rationale: Medication error corrected quickly; patient experienced no lasting harm.
```

**`final_report.json`**  
Example:
```json
{
  "classification": "NSE",
  "severity": "Non-Safety Event",
  "rationale": "No deviation from standard medical procedure."
}
```

This file will appear automatically under `/src`.

---

## How It Works Internally

| Component | Function |
|------------|-----------|
| `main.py` | Entry point — manages all pipeline stages |
| `ingestion.py` | Accepts text input | 
| `llm_classify.py` | Sends request to Gemini or OpenAI and parses model response |
| `report.py` | Saves classification result as JSON |

