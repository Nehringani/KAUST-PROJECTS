# ThreatLens — Injection-Resilient Threat Intelligence Synthesis Pipeline

**Author:** Nehrin Gani · KAUST VSRP · CyberSaR Laboratory
**Language:** Python 3.10+
**Recommended IDE:** Visual Studio Code

---

# Complete Guide (Step by Step for Beginners)

> All code, comments, and the interface are in **English**. This guide explains how to set up and run the project step by step.

## 1. Project Objective

ThreatLens is a **threat intelligence aggregation pipeline with a three-layer defense** against *indirect prompt injection* attacks.

It:

1. Reads real public feeds from CISA and abuse.ch URLhaus, along with 20 simulated samples containing injection payloads.
2. Passes each item through three defense layers: preprocessing, PromptShield, and schema validation.
3. Synthesizes threat reports using an LLM, or a free offline *mock mode*.
4. Runs an experiment that **measures how much each layer individually contributes** to defending against injection attacks.
5. Displays the results in a **Streamlit dashboard** for the analyst.

---

## 2. Tools You Need to Install

Everything required to run the project is free.

| Tool                           | What It Is For            | Link                                                |
| ------------------------------ | ------------------------- | --------------------------------------------------- |
| **Python 3.10+**               | Running the code          | https://www.python.org/downloads/                   |
| **Visual Studio Code**         | Code editor (IDE)         | https://code.visualstudio.com/                      |
| **Python Extension (VS Code)** | Python support in VS Code | Install it inside VS Code from the *Extensions* tab |
| **Git** *(optional)*           | Version control           | https://git-scm.com/downloads                       |

No paid API key is required. The project can run completely free in **mock mode**, where the *synthesizer* returns simulated JSON.

If you want to use a real LLM, you can optionally configure a free API key from OpenRouter or Groq. See `.env.example` for configuration details.

---

## 3. Steps to Run the Project

Open the **Command Prompt** on Windows or the **Terminal** on macOS/Linux.

```bash
# 1) Extract the project ZIP file and enter the project folder
cd threatlens

# 2) Create a virtual environment to isolate the project dependencies
python -m venv .venv

# 3) Activate the virtual environment

# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate

# 4) Upgrade pip and install the required dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5) Optional: copy .env.example to .env if you want to use a real LLM

# macOS / Linux:
cp .env.example .env

# Windows:
copy .env.example .env
```

---

## 4. How to Run Each Part of the Project

### a) Run the Experiment That Measures the Contribution of Each Defense Layer

This generates a CSV file inside the `results/` directory.

```bash
python -m src.threatlens.experiment
```

**Expected output:** A table containing the different defense conditions and their injection success rates:

* No defense
* Layer 1 only
* Layer 2 only
* Layer 3 only
* All 3 layers

---

### b) Run the Streamlit Dashboard

This launches the visual interface for the analyst.

```bash
streamlit run dashboard/app.py
```

Then open your browser at:

```text
http://localhost:8501
```

---

### c) Run the Tests

```bash
pytest -q
```

---

## 5. Project Structure

```text
threatlens/
├── README.md                    ← This file
├── requirements.txt             ← Python dependencies
├── .env.example                 ← Environment variables (optional LLM configuration)
├── src/
│   └── threatlens/
│       ├── config.py                ← Configuration and project paths
│       ├── feeds.py                 ← RSS/CSV feed fetching (CISA, URLhaus)
│       ├── simulated_feeds.py       ← 20 feeds containing injection payloads
│       ├── layer1_preprocessing.py  ← LAYER 1 — cleaning and heuristics
│       ├── layer2_promptshield.py   ← LAYER 2 — classifier (rules + lightweight ML)
│       ├── layer3_schema.py         ← LAYER 3 — Pydantic ThreatIntelReport validation
│       ├── synthesizer.py           ← LLM call with free mock fallback
│       ├── pipeline.py              ← Orchestrates the three defense layers
│       ├── experiment.py            ← Measures the contribution of each layer
│       └── logging_utils.py         ← Structured logging
├── dashboard/
│   └── app.py                      ← Streamlit dashboard
├── tests/
│   └── test_pipeline.py            ← Unit tests
├── data/                           ← Feed cache
├── results/                        ← Experiment CSV files and metrics
└── docs/                           ← Additional documentation
```

---

## 6. Expected Results

After running:

```bash
python -m src.threatlens.experiment
```

You should obtain the following file:

```text
results/defense_contribution.csv
```

Example expected results:

| Condition    | Injection Success Rate |
| ------------ | ---------------------: |
| No defense   |                ~85–90% |
| Layer 1 only |                ~50–60% |
| Layer 2 only |                ~20–30% |
| Layer 3 only |                ~40–50% |
| All 3 layers |              **< 10%** |

These results demonstrate the **marginal contribution of each defense layer**.

The experiment helps identify how much each individual defense mechanism contributes to reducing prompt injection success and provides the empirical findings supporting the project's research and portfolio claims.

---

## 7. Common Problems

### `"python" is not recognized`

Reinstall Python and make sure to check:

```text
Add Python to PATH
```

during the installation process.

---

### `ModuleNotFoundError`

Make sure the virtual environment is activated before running the project.

**Windows:**

```powershell
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

---

### CISA or URLhaus Feed Fails

This can happen if you are offline or if the external feed is temporarily unavailable.

The experiment can still run because it uses locally stored simulated samples.

---

### Streamlit Does Not Open

Make sure Streamlit is installed:

```bash
pip install streamlit
```

Also make sure that port `8501` is available.

---

# English Project Summary

For the full technical description of the project, see:

```text
docs/PROJECT.md
```

