# AC215 - Milestone4

## Team Members
Zilong Wang, Jingxi Zhang, Bruce Zhou, Alice Zhang

## Group Name
AC215_888

## Project Goal
Design and build a web-based tool that uses large language models to help hospitals and healthcare staff efficiently and accurately classify safety incident reports following the HPI methodology.


## Milestone 4

In Milestone 4, we combined the backend, frontend, and supporting services into a complete, locally testable system and prepared the entire application to run reliably and be packaged for future deployment.


### Data Versioning and Reproducibility

To ensure reproducibility and maintainability, we will implement a snapshot-based data versioning workflow tailored to hospital policy documents. All policy files used in retrieval (RAG), classification prompts, and decision logic are stored as timestamped snapshots in a Google Cloud Storage bucket.

This approach fits our project because hospital policies are mostly static but may undergo major updates. Snapshot-based versioning allows us to:

1. preserve historical policy states for auditing,

2. reproduce earlier model outputs, and

3. understand how policy revisions impact classification behavior.

Snapshot naming scheme:

```
policies_v1/   # initial policy set
policies_v2/   # updated discharge rules
policies_v3/   # new safety reporting guidelines
```

Reproducing a past version:

```
gsutil cp -r gs://ac215-888-artifacts/policies_v2/ data/policies/
```

Our policy documents evolve infrequently and in large, discrete updates (a static-to-semi-static dataset), making snapshot-based versioning more appropriate than diff-based tools; this ensures that every model run is tied to an exact policy version, supporting full reproducibility across time.


### Model Training or Fine-Tuning

Our current system relies on prompt engineering and RAG for safety-event classification. Prompts encode our decision logic and incorporate relevant hospital policy excerpts. This approach enables rapid iteration, strong interpretability, and avoids the computational overhead of model training.

In future iterations, we plan to explore:

- Supervised fine-tuning using labeled safety-event datasets

- Parameter-efficient fine-tuning (e.g., LoRA) for hospital-specific reasoning

- Comparisons between fine-tuned models and current prompt-based workflows, focusing on:

  - Accuracy

  - Robustness to policy updates

  - Reproducibility under versioned datasets

  - Cost and compute considerations

All datasets, prompts, and configuration files will continue to be versioned to ensure fully reproducible evaluation.

