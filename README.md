# AC215 - Milestone2

## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang

## Group Name
AC215_888

## Project Goal
Design and build a web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI methodology.

## Milestone 2
In this milestone, we completed the implementation of two important components of our project:

1. Data Generation
2. Safety event classification




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

### Prerequisites:

Before running the program, make sure you have:

- Docker Desktop installed and running

- A valid Google service account key (e.g. llm-service-account.json)

- Your should change your working directory into `src\datapipeline` by typing the command line below in your terminal

```bash
cd src/datapipeline
```

### Step 1. Build the Docker Image

Run this command from the folder containing your `Dockerfile`:

```bash
docker build -t project_data -f Dockerfile .
```

### Step 2. Run the Docker Container
You need to mount two folders into the container:
- Project folder → contains your Python code
- Secrets folder → contains your credentials (e.g., llm-service-account.json)

```bash
docker run --rm -ti `
  -v "YourPath\project_folder:/app" `
  -v "YourPath\secrets_folder:/app/secrets" `
  project
```

### Step 3. Run the Python Script
Inside the container, run:
```bash
python data_generation.py
```
This will use Genimi to generate medical incidents data

## Safety Event Classification

### Prerequisites 

Before running the program, make sure you have:

- Docker Desktop installed and running

- A valid Google service account key (e.g. llm-service-account.json). This service account should at least have Vertex AI access.

- Your should change your working directory to `src/model` by typing the command line below in your terminal

```bash
cd src/model
```

### Step 1. Build the Docker Image
Run this command from the folder containing the `Dockerfile`:

```bash
docker build -t prompt_chaining -f Dockerfile .
```

This will:
1. Install Python 3.11 + system dependencies  
2. Create a non-root user (`app`)  
3. Copy project files from  `/src/model`
4. Install dependencies via `uv sync`

### Step 2. Run the Docker Container
You need to mount two folders into the container:
- Project folder → contains your Python code. This is typically your currently working directory since we have asked you to `cd` into `src/model`
- Secrets folder → contains your credentials (e.g., llm-service-account.json). You can choose to store it anywhere you want but by default we assume you stored it under `AC215_888/secrets`.

Example command lines:

```bash
docker run --rm -ti \
  -v "$(pwd):/app" \
  -v "$(pwd)/../../secrets:/secrets" \
  prompt_chaining
```

### Step 3. Run the Python Scripts

In this milestone, we have implemented two features for the purpose of our project.

1. **`prompt_utils.py`**
  Thi





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

## RAG Implementation

Our next step is to integrate RAG component into Prompt 1. This enhancement will allow the model to retrieve relevant mock hospital policies, clinical guidelines, and best-practice standards before generating its final classification.

---

## How It Works Internally

| Component | Function |
|------------|-----------|
| `main.py` | Entry point — manages all pipeline stages |
| `ingestion.py` | Accepts text input | 
| `llm_classify.py` | Sends request to Gemini or OpenAI and parses model response |
| `report.py` | Saves classification result as JSON |

