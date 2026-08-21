# AgentGuard

**Security Evaluation Framework for Multi-Step LLM Agents in SOC Environments**

AgentGuard is a research framework that measures how susceptible multi-step LLM agents, used in Security Operations Center (SOC) automation, are to prompt injection attacks placed at different positions in a reasoning chain and delivered through different tool types.

The framework tests:

* **4 injection positions:** `pre-task`, `mid-task`, `late-task`, `cross-tool`
* **4 tool types:** `web_search`, `file_reader`, `code_executor`, `communication`
* **20 legitimate SOC tasks** used as a baseline
* **16 injection scenarios** (4 positions × 4 tools)

It outputs a JSON/CSV report, plus a bar chart of *Attack Success Rate by Position* and a heatmap of *Position × Tool*.

---

# 1. Project Goal

Modern Security Operations Center (SOC) automation increasingly relies on LLM agents that autonomously call tools such as searching the web, reading log files, running code, and sending messages.

A malicious payload can be hidden inside any tool's **output**, not only in the user's original prompt.

AgentGuard quantifies **where** in the reasoning chain those injections are most effective, producing a position-sensitivity study for agentic SOC workflows.

---

# 2. How to Run the Project

> This guide is designed for someone who has **never programmed before**. Follow the steps in order.

## 2.1. Tools You Need to Install

| Tool                            | What It Is For                            | Link                                                                                           |
| ------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Python 3.10+**                | Programming language used for the project | https://www.python.org/downloads/                                                              |
| **Visual Studio Code**          | Code editor (IDE)                         | https://code.visualstudio.com/                                                                 |
| **Python Extension (VS Code)**  | Python support in VS Code                 | Install it inside VS Code from the **Extensions** tab by searching for **Python** by Microsoft |
| **Git** *(optional)*            | Cloning and version control               | https://git-scm.com/downloads                                                                  |
| **OpenAI Account** *(optional)* | Running the agent with a real LLM         | https://platform.openai.com/                                                                   |

> **No API key? No problem.**
>
> The project includes a built-in `FakeListLLM` that simulates the agent completely free of charge.
>
> Simply run the project using `--provider fake`, which is the default option. You only need an OpenAI API key if you want to test the project against a real GPT model.

---

## 2.2. Step-by-Step Instructions

### Step 1 — Install Python

1. Download Python from:
   https://www.python.org/downloads/

2. During installation on Windows, **check the box that says "Add Python to PATH"**.

3. Confirm that Python was installed correctly by opening a terminal and typing:

```bash
python --version
```

---

### Step 2 — Install Visual Studio Code

1. Download Visual Studio Code from:
   https://code.visualstudio.com/

2. Open VS Code.

3. Go to the **Extensions** tab.

4. Install the following extensions:

   * `Python` by Microsoft
   * `Pylance` by Microsoft

---

### Step 3 — Open the Project

1. Extract the `AgentGuard.zip` file.

2. In VS Code, go to:

```text
File → Open Folder...
```

3. Select the `AgentGuard` folder.

---

### Step 4 — Create a Virtual Environment

Open the integrated VS Code terminal:

```text
Terminal → New Terminal
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 5 — Install the Dependencies

Run:

```bash
pip install -r requirements.txt
```

---

### Step 6 — Optional: Configure Your OpenAI API Key

If you want to run the project against a **real GPT model** instead of the simulated LLM:

1. Create an account at:

   https://platform.openai.com/

2. Go to **API Keys** and generate a new API key.

3. Copy the `.env.example` file and rename it to:

```text
.env
```

4. Add your API key:

```text
OPENAI_API_KEY=sk-...
```

> **Important:** API usage may involve costs depending on your model and account billing.
>
> The project can also be run entirely for free using the fake provider.

---

### Step 7 — Run the Evaluation

#### Free Mode

This uses the simulated LLM and requires no API key:

```bash
python -m agentguard.run_evaluation --provider fake
```

#### Real Mode

This uses a real OpenAI model:

```bash
python -m agentguard.run_evaluation --provider openai --model gpt-3.5-turbo
```

---

### Step 8 — View the Results

After the evaluation finishes, the following files will be generated:

* `results/results.json` — All raw evaluation results
* `results/results.csv` — The same results in CSV format
* `results/asr_by_position.png` — Attack Success Rate bar chart
* `results/asr_position_tool_heatmap.png` — Position × Tool heatmap
* `results/report.md` — Report containing the conclusions

---

### Step 9 — Run the Tests

To run the optional test suite:

```bash
pytest -q
```

---

# 3. Technical Documentation

## Repository Layout

```text
AgentGuard/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── agentguard/
│   ├── __init__.py
│   ├── config.py
│   ├── llm_provider.py
│   ├── agent.py
│   ├── injections.py
│   ├── evaluator.py
│   ├── run_evaluation.py
│   ├── plotting.py
│   └── tools/
│       ├── __init__.py
│       ├── web_search.py
│       ├── file_reader.py
│       ├── code_executor.py
│       └── communication.py
├── scenarios/
│   ├── legitimate_tasks.json
│   └── injection_scenarios.json
├── tests/
│   └── test_smoke.py
├── docs/
│   └── methodology.md
└── results/
    # Generated at runtime
```

---

# Architecture

`run_evaluation.py` iterates over every `(position, tool)` pair, runs the matching legitimate task, injects the payload into the target tool's output at the selected chain position, and asks a *judge* whether the final agent output complied with the injection.

Results are aggregated into:

* A per-position **Attack Success Rate (ASR)**
* A **Position × Tool heatmap**

For the full experimental protocol, see:

```text
docs/methodology.md
```

---

# License

MIT — for academic and research use.
