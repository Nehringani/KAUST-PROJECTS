# ConstitutionBench — Constitutional AI for Cybersecurity SOC Assistants

> Benchmarking Constitutional AI (CAI) principle design for LLM-based SOC
> assistants — evaluating **helpfulness vs. adversarial resistance** on a
> dataset of dual-use cybersecurity queries.
>
> Author: Nehrin Gani · KAUST VSRP Application · CyberSaR Lab
> Status: Research prototype · Runtime: API-only (no GPU) · Est. cost: ~US$15–25

---

## Overview

This project evaluates whether **Constitutional AI principles** (rules written
in natural language that guide an LLM) work well when applied to a
**Security Operations Center (SOC) assistant**. It:

1. Defines **3 different constitutions** (general-purpose, cybersecurity, and
   hardened against adversarial attacks).
2. Applies each one to **100 dual-use queries** (questions that are legitimate
   for a security analyst but potentially dangerous if misused).
3. Runs a **CAI pipeline (self-critique + revise)** using an LLM API.
4. Evaluates each response across **4 dimensions**: helpfulness, resistance,
   consistency, and coverage.
5. Generates **charts and a report** with the findings, including dead
   principles and conflicting principles.

## Requirements

| Tool | Purpose | Link |
|---|---|---|
| **Python 3.10+** | Project programming language | https://www.python.org/downloads/ |
| **Visual Studio Code** | Recommended editor | https://code.visualstudio.com/ |
| **Python Extension (VS Code)** | Python support in the editor | VS Code Marketplace |
| **Git** (optional) | Version control | https://git-scm.com/ |
| **An LLM API key** | To call Claude or GPT-4 | See API configuration below |

> ⚠️ The only paid components are the **API calls**. The estimated cost for
> running the full benchmark is US$15–25. A smaller run with 10 sample queries
> can cost approximately US$1.

---

## Installation

### 1. Install Python

Download Python 3.10 or later from:

https://www.python.org/downloads/

On Windows, select **"Add Python to PATH"** during installation.

Verify the installation:

```bash
python --version

2. Install VS Code and the Python Extension

Install Visual Studio Code:

https://code.visualstudio.com/

Open VS Code, go to the Extensions tab (Ctrl+Shift+X), search for
Python by Microsoft, and install it.

3. Open the Project
Extract the constbench.zip file.
Open VS Code.
Select File → Open Folder.
Choose the constbench folder.
4. Create a Virtual Environment

Open the integrated terminal in VS Code (`Ctrl+``).

Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

If Windows displays a script execution error, run:

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
5. Install Dependencies
pip install -r requirements.txt
API Configuration

The project supports either Anthropic Claude or OpenAI models.

Anthropic Claude

Create an account at:

https://console.anthropic.com/

Go to API Keys → Create Key.
Copy the API key.
Add API credits.
OpenAI

Create an account at:

https://platform.openai.com/

Go to API Keys → Create Secret Key.
Copy the generated API key.
Configure the Environment

In the project root, copy the example file:

macOS / Linux
cp .env.example .env
Windows
copy .env.example .env

Open .env and add your API key:

ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
# OPENAI_API_KEY=sk-xxxxxxxxxxxxx

Do not commit your .env file or API keys to GitHub.

Running the Benchmark
Quick Test

Run the benchmark on five queries:

python -m src.run_benchmark --sample 5
Full Benchmark

Run all 100 queries across the three constitutions:

python -m src.run_benchmark
Generate Analysis

Generate charts and the final report:

python -m src.analyze

Results are saved to:

results/*.json — raw benchmark results
analysis/plots/*.png — generated charts
analysis/report.md — final analysis report

constbench/
├── README.md                        # this file
├── requirements.txt                 # Python dependencies
├── .env.example                     # API key configuration template
├── constitutions/                   # 3 constitutions in YAML
│   ├── general_purpose_v1.yaml
│   ├── cybersecurity_v1.yaml
│   └── adversarially_hardened_v1.yaml
├── data/
│   └── dual_use_queries.csv         # 100 dual-use queries
├── src/
│   ├── llm_client.py                # wrapper for Claude/OpenAI
│   ├── constitution.py              # loads and validates YAML
│   ├── cai_pipeline.py              # generate → critique → revise
│   ├── evaluator.py                 # evaluation across 4 dimensions
│   ├── run_benchmark.py             # main entrypoint
│   └── analyze.py                   # generates charts and report
├── results/                         # output JSON (generated)
└── analysis/                        # charts + report (generated)

