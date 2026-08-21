# Research Log — PromptShield

Weekly notes on decisions, dead-ends, and observations. Update every Friday.

## Week 1 — Taxonomy & Seed Dataset
- Drafted the 8-class taxonomy (see `data/taxonomy/injection_taxonomy_v1.md`).
- Hand-crafted 25+ seed examples per class.
- Decision: SOC context field is required in every row to enable per-context error analysis.

## Week 2 — Public Sources & Augmentation
- Sources reviewed: Perez & Ribeiro 2022, BIPIA (Microsoft), PromptBench, JailbreakHub.
- Filter: only examples that map to one of the 8 SOC classes were retained.
- Deterministic augmentation implemented in `src/data/preprocessor.py` (offline, no API cost).

## Week 3 — Training
- Base model: `roberta-base`, num_labels=2.
- Hyperparameters: epochs=5, batch=16, lr=2e-5, warmup=100, fp16=True.
- Early stopping on validation F1, patience=2.
- Primary metric tracked in `compute_metrics`: **False Negative Rate**.

## Week 4 — Evaluation & Deployment
- Held-out test set (15%) evaluation only — never re-tuned on it.
- Latency measured on CPU and GPU (p50/p95/p99).
- Two-stage `PromptShield` detector: regex rules → RoBERTa classifier.
- Transfer test: run the detector on outputs targeting 3 different LLMs.

## Dead-ends / Notes
- (fill in as you go)
