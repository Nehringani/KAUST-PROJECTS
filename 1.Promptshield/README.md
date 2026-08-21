# PromptShield
A Taxonomy and Detection Framework for Prompt-Injection Attacks Against LLM-Based Cybersecurity Assistants

Author: Nehrin Gani · KAUST VSRP Application · CyberSaR Lab
Status: In development · Timeline: 3–4 weeks · Compute: Google Colab Free Tier (T4 GPU)

---

## 1. Research Problem

There is no open benchmark or detection framework tailored to prompt-injection attacks in SOC (Security Operations Center) LLM deployments. Generic injection taxonomies ignore cybersecurity-specific attack vectors that appear when LLMs process SIEM logs, threat-intelligence reports, and malware analysis data — environments where the model is expected to process attacker-controlled content as part of its core function.

## 2. Core Contribution

1. An **8-class injection taxonomy** for cybersecurity contexts (see `data/taxonomy/injection_taxonomy_v1.md`).
2. A **hand-labeled dataset** of 1,000+ SOC-context examples (`data/processed/`).
3. A **fine-tuned RoBERTa classifier** deployable as a pre-inference triage layer (`src/detection/shield.py`).

## 3. Primary Metric

**False Negative Rate (FNR)** — undetected injections. This is the critical security measure and takes precedence over F1 or accuracy.

## 4. The 8-Class Taxonomy (summary)

| # | Class | Vector | Frequency | Severity |
|---|-------|--------|-----------|----------|
| 1 | Direct Override | Embedded in analyst queries | High | High |
| 2 | Role Assumption | Hidden in threat reports | Medium | High |
| 3 | Indirect Document | SIEM logs, CVE descriptions, malware samples | Low | Critical |
| 4 | Multi-Turn Erosion | Long analyst sessions (conversation-level) | Very Low | High |
| 5 | Encoding Obfuscation | Base64/ROT13 in malware strings | Medium | Medium-High |
| 6 | Hypothetical Distancing | Escalating threat-modeling requests | Medium | Medium |
| 7 | Authority Claim | False admin/pentest authorization | High | Medium |
| 8 | Context-Window Poisoning | False context pre-positioned in long reports | Low | High |

## 5. Repository Structure

```
promptshield/
├── README.md
├── RESEARCH_LOG.md
├── requirements.txt
├── data/
│   ├── raw/                    Public datasets (do not modify)
│   ├── processed/
│   │   ├── cybersec_injections_v1.csv   Hand-crafted dataset
│   │   └── augmented_dataset.csv
│   └── taxonomy/
│       └── injection_taxonomy_v1.md
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_taxonomy_development.ipynb
│   ├── 03_classifier_training.ipynb     Main Colab notebook
│   └── 04_evaluation_analysis.ipynb
├── src/
│   ├── data/preprocessor.py
│   ├── models/classifier.py
│   ├── models/trainer.py
│   ├── evaluation/metrics.py
│   └── detection/shield.py              Deployable detection layer
└── results/
    ├── classification_report.json
    ├── confusion_matrix.png
    └── taxonomy_coverage_analysis.md
```

## 6. Evaluation Targets

| Metric | Target | Description |
|--------|--------|-------------|
| Binary F1 | > 0.85 | Overall classification quality |
| False Negative Rate | < 10% | PRIMARY — missed injections |
| False Positive Rate | < 15% | Legitimate queries blocked |
| p95 inference latency | < 50 ms | SOC operational viability |
| Per-class F1 | Report all 8 | Detection difficulty per class |
| Transfer test | 3 models | Cross-LLM generalisation |

## 7. Quickstart (local, Python 3.10+)

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.data.preprocessor     # build augmented dataset
python -m src.models.trainer        # fine-tune RoBERTa (needs a GPU for speed)
python -m src.evaluation.metrics    # print full evaluation report
python -m src.detection.shield      # demo of the two-stage detector
```

For the full step-by-step Portuguese execution guide (VS Code + Google Colab), see **`COMO_EXECUTAR.md`**.

## 8. Licence

MIT (research prototype — not a production security control on its own).
