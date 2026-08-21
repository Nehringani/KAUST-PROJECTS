# JailbreakMap

**Longitudinal Analysis of Jailbreak Technique Evolution and Constitutional Resistance**

Temporal study of 1,000+ jailbreaks across three years — mapping the LLM attack–defense arms race.

- Author: Nehrin Gani
- Affiliation: KAUST VSRP Application · CyberSaR Laboratory
- Language: Python 3.10+
- Compute: CPU only (no GPU required)
- Estimated cost: ~$0–5

---

## 1. Project Objective

There is currently **no systematic longitudinal analysis** of how jailbreak technique complexity has increased over time, nor whether Constitutional AI training keeps pace with this evolution.

**JailbreakMap** fills this gap by:

1. Collecting 1,000+ documented jailbreak prompts with timestamps.
2. Mapping each prompt to an 8-class injection taxonomy (PromptShield-style) + optional 9th emerging class.
3. Producing an empirical **evolution graph** of the attack–defense arms race.
4. Measuring **constitutional coverage gaps** — which attack classes have no matching defensive principle.
5. Providing the empirical foundation for **Adaptive Constitutional AI** research.

The full analysis pipeline runs on a laptop in a few minutes.

---

## 2. Output artifacts

After running the pipeline you will get, under `outputs/`:

- `figures/fig1_complexity_over_time.png` — mean prompt complexity per month
- `figures/fig2_class_distribution_by_year.png` — stacked bars, technique class × year
- `figures/fig3_evolution_graph.png` — NetworkX co-occurrence graph
- `figures/fig4_constitutional_coverage_heatmap.png` — class × time gap map
- `figures/fig5_success_rate_decay.png` — synthetic/observed decay curves
- `tables/technique_class_by_month.csv`
- `tables/coverage_gaps.csv`
- `tables/summary_findings.md`
- `processed/jailbreakmap_dataset.csv` — the labelled dataset (open output)

---

## 3. Repository layout

```
JailbreakMap/
├── README.md                 # this file (English)
├── COMO_EXECUTAR.md          # step-by-step instructions in Portuguese
├── requirements.txt
├── .gitignore
├── config.yaml               # tunable parameters
├── src/
│   ├── __init__.py
│   ├── taxonomy.py           # 8+1 class definitions & keyword rules
│   ├── constitution.py       # cybersecurity constitutional principles
│   ├── data_loader.py        # step 1: load & clean sources
│   ├── classify.py           # step 2: keyword-based class assignment
│   ├── cluster.py            # step 3: SentenceTransformer + KMeans
│   ├── temporal.py           # step 4: monthly complexity metrics
│   ├── graph.py              # step 5: NetworkX evolution graph
│   ├── coverage.py           # step 6: constitutional gap analysis
│   ├── decay.py              # step 7: success rate decay
│   ├── report.py             # step 8: write findings
│   ├── visualize.py          # all figure generators
│   └── run_pipeline.py       # end-to-end orchestrator
├── data/
│   ├── raw/                  # put downloaded CSVs here
│   └── processed/
├── notebooks/
│   └── exploration.ipynb     # optional manual review
├── outputs/
│   ├── figures/
│   └── tables/
└── tests/
    └── test_smoke.py
```

---

## 4. Quickstart (English)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.run_pipeline --synthetic   # runs end-to-end on bundled synthetic data
```

Then check `outputs/figures/` and `outputs/tables/`.

To run against real data, drop the JailbreakHub CSV into `data/raw/jailbreakhub.csv` and run:

```bash
python -m src.run_pipeline
```

See **COMO_EXECUTAR.md** for a beginner-friendly walkthrough in Portuguese.

---

## 5. Data sources

| Source | Description | Link |
|---|---|---|
| JailbreakHub | Real-world jailbreak prompts w/ dates | https://github.com/verazuo/jailbreak_llms |
| WildJailbreak | Ding et al., 2024 — deployment attempts | https://arxiv.org/abs/2406.18510 |
| HarmBench | Standardized red-team benchmark | https://github.com/centerforaisafety/HarmBench |
| arXiv 2022–2025 | Manual annotation of 15+ jailbreak papers | — |

The pipeline runs with **any subset** of these — if a file is missing it is skipped and the run continues with what is available (or with the synthetic dataset).

---

## 6. License

Released under the MIT License. See `LICENSE`.
