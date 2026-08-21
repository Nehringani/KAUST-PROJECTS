# SOC-RedTeam

**Automated Red Teaming Framework for Security Operations LLM Assistants**

SOC-RedTeam is a modular framework that measures how well a Security Operations
Center (SOC) LLM assistant resists prompt injection attacks embedded in realistic
SOC content: SIEM alerts, threat intelligence reports, malware analysis reports,
and analyst chat queries.

The framework runs four attack modules (direct injection, indirect embedding,
multi-turn erosion, encoding obfuscation) against a target model, uses a
judge LLM to decide whether each attack succeeded, stores all results in a
SQLite database, and visualises them in a Streamlit dashboard.

---

## 1. Project Objective

- Provide a **quantitative, reproducible** measurement of how vulnerable a SOC
  LLM assistant is to prompt-injection attacks.
- Compare the same target model **with and without** defense layers
  (`none`, `promptshield`, `dpo_guard`, `both`).
- Break results down by **attack module × attack class × SOC context** so
  researchers can see exactly where a defense helps and where it fails.
- Provide a **self-contained Python project** that can run on a laptop
  with a free-tier API key or a fully local Ollama model.

---

## 2. Repository Layout

```text
SOC-RedTeam/
├── README.md
├── requirements.txt
├── .env.example
├── configs/
│   └── default.yaml           # Which target, judge, defenses, sample sizes
├── src/
│   ├── attacks/               # 4 attack modules
│   │   ├── direct_injector.py
│   │   ├── indirect_embedder.py
│   │   ├── multi_turn_eroder.py
│   │   └── encoding_obfuscator.py
│   ├── contexts/              # SOC content templates
│   │   ├── siem.py
│   │   ├── threat_report.py
│   │   ├── malware.py
│   │   └── analyst.py
│   ├── target/                # Target-model wrapper (OpenAI / Anthropic / Ollama)
│   │   └── target_model.py
│   ├── judge/                 # Judge LLM: did the attack succeed?
│   │   └── compliance_detector.py
│   ├── defenses/              # Optional defense layers
│   │   ├── prompt_shield.py
│   │   └── dpo_guard.py
│   ├── db/
│   │   └── results_db.py      # SQLite schema + insert/query helpers
│   ├── utils/
│   │   ├── llm_client.py      # Unified LLM client (OpenAI/Anthropic/Ollama)
│   │   └── logging_utils.py
│   └── runner.py              # Orchestrates the full evaluation
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── database/                  # results.db lands here at runtime
├── tests/
│   ├── test_attacks.py
│   ├── test_judge.py
│   └── test_db.py
├── data/prompts/              # Static attack phrase lists
└── docs/
    └── ARCHITECTURE.md

How to Run the Project
3.1. Required Tools

Python 3.10 or later — https://www.python.org/downloads/

During installation on Windows, check the "Add Python to PATH" box.

Visual Studio Code — https://code.visualstudio.com/

Recommended extensions, available from the Extensions panel:

Python (Microsoft)
Pylance
SQLite Viewer (optional, for opening database/results.db)
Git (optional) — https://git-scm.com/downloads
An LLM provider (choose ONE):

Ollama (100% free, local, recommended) — https://ollama.com/download

After installation, run:

ollama pull llama3.1:8b
OpenAI — https://platform.openai.com/api-keys
Anthropic — https://console.anthropic.com/
3.2. Set Up the Project

Open a terminal (PowerShell on Windows, Terminal on macOS/Linux):

# 1. Go to the project folder
cd SOC-RedTeam


# 2. Create a virtual environment
python -m venv .venv


# 3. Activate the virtual environment


# Windows PowerShell:
.venv\Scripts\Activate.ps1


# Windows cmd:
.venv\Scripts\activate.bat


# macOS / Linux:
source .venv/bin/activate


# 4. Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt


# 5. Copy the secrets configuration file


# Windows:
copy .env.example .env


# macOS / Linux:
cp .env.example .env

Open the .env file and choose your provider:

Local Ollama:

LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b

OpenAI:

LLM_PROVIDER=openai
OPENAI_API_KEY=sk-....
OPENAI_MODEL=gpt-4o-mini

Anthropic:

LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-....
ANTHROPIC_MODEL=claude-3-5-haiku-latest
3.3. Open the Project in Visual Studio Code
Open VS Code.
Select File > Open Folder….
Choose the SOC-RedTeam folder.
Select the Python interpreter associated with .venv.
Open an integrated terminal (Ctrl + '). The virtual environment should already be active.
3.4. Run the Tests
pytest -q

The tests use an internal fake LLM, so they run without consuming API credits.

3.5. Run the Full Evaluation
python -m src.runner --config configs/default.yaml

This will:

Generate the attacker × context × defense combinations.
Call the target model for each attack.
Call the judge model to classify the response.
Store each result in database/results.db.

For a smaller test run, use --samples 5:

python -m src.runner --config configs/default.yaml --samples 5
3.6. View the Dashboard
streamlit run dashboard/app.py

Open http://localhost:8501.

The dashboard shows:

Success rate by attack module
Success rate by SOC context
Comparison between defense configurations (none / promptshield / dpo_guard / both)
A detailed table of all attacks
3.7. Costs
Local Ollama: €0
OpenAI gpt-4o-mini: a full run (~200 attacks) typically costs less than $1 USD
Anthropic Haiku: similar cost
4. Attack Modules
Module	Class(es)	Description
DirectInjector	1, 2, 6, 7	Explicit override and role-assumption phrases combined with analyst queries.
IndirectEmbedder	3	Payloads hidden inside SIEM logs, threat reports, and malware reports.
MultiTurnEroder	4	A 5-turn escalating conversation that shifts the model's baseline.
EncodingObfuscator	5	Base64 / ROT13 / Unicode-homoglyph obfuscation of payloads.
5. Judge Model

src/judge/compliance_detector.py implements the judge using the prompt from
the project brief. Output is a strict JSON object:

{
  "attack_succeeded": true,
  "compliance_type": "full|partial|superficial|none",
  "injection_identified": false,
  "attack_success_score": 0.0
}
6. Database Schema

See src/db/results_db.py and docs/ARCHITECTURE.md. Key query:

SELECT defense_applied,
       AVG(attack_succeeded) AS success_rate,
       COUNT(*)              AS total_attacks
FROM   experiments
GROUP  BY defense_applied;
7. Extending
Add a new attack module: drop a file in src/attacks/, subclass
AttackModule, and register it in src/runner.py.
Add a new SOC context: drop a file in src/contexts/, and expose a
render(payload: str) -> str function.
Add a new defense: drop a file in src/defenses/, and expose
apply(prompt: str) -> tuple[str, bool].
8. License

MIT. For academic and research use.
