# AC215 - Milestone2 
## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang
## Group Name
AC215_888
## Project
Design and build a web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI methodology.


## Data


## RAG Implementation



## Running Dockerfile
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

