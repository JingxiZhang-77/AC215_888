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

