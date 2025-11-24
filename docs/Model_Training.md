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


