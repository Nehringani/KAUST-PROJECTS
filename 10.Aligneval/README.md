# AlignEval

**Personal Research Dashboard for Tracking LLM Alignment Technique Performance**

AlignEval is the meta-project of a 10-project LLM security portfolio. It provides a unified Streamlit dashboard and a single SQLite results database that aggregates evaluation results across every other project, enabling temporal tracking, Pareto analysis, and defense-in-depth comparison from one place.

> Nehrin Gani · KAUST VSRP Application · CyberSaR Laboratory

---

## What the Dashboard Shows

| # | View                        | Purpose                                                                      |
| - | --------------------------- | ---------------------------------------------------------------------------- |
| 1 | **Overview**                | 4 KPI cards and a timeline scatter plot of every experiment                  |
| 2 | **DPO-Guard Pareto**        | Helpfulness vs. injection resistance, β-labeled, with a Pareto frontier line |
| 3 | **Defense Stack**           | Attack success rate by defense configuration (`none → all-three`)            |
| 4 | **Temporal Tracking**       | How each metric evolves across iterations                                    |
| 5 | **Unlearning Completeness** | Heatmap of knowledge target × retrieval vector                               |
| 6 | **Log New Result**          | Data-entry form that writes directly to SQLite                               |

---

## Standardized Metric Taxonomy

Every project in the portfolio logs into `database/results.db` using this fixed set of metric names (see `database/db.py`):

```text id="eaqtx0"
injection_resistance_rate   # Projects 1, 3, 5, 6, 9
false_negative_rate         # Project 1
helpfulness_retention       # Projects 2, 3
f1_score                    # Project 1
unlearning_completeness     # Project 4
attack_success_rate         # Projects 5, 8
constitutional_coverage     # Project 2
consistency_score           # Project 2
ttp_extraction_accuracy     # Project 6
```

All metric values are normalized to the range `[0.0, 1.0]`.

---

## Project Layout

```text id="zw58av"
aligneval/
├── dashboard/
│   └── app.py                 # Streamlit entry point with 6 views
├── database/
│   ├── db.py                  # Schema and log_result / log_unlearning_cell
│   └── results.db             # Created automatically on first run
├── scripts/
│   ├── seed_dummy_data.py     # Populates the database with realistic demo data
│   └── test_logging.py        # Smoke test for the database layer
├── screenshots/               # Store dashboard screenshots for the README
├── requirements.txt
└── README.md
```

---

# How to Run the Project

> This guide is designed for someone who has **never programmed before**. Follow the steps in order.

All code, comments, file names, and the dashboard interface are in English.

## 1. Tools You Need to Install

All required tools are free.

| Tool                             | What It Is For       | Where to Get It                                                                          |
| -------------------------------- | -------------------- | ---------------------------------------------------------------------------------------- |
| **Python 3.10+**                 | Running the code     | https://www.python.org/downloads/                                                        |
| **Visual Studio Code**           | Code editor          | https://code.visualstudio.com/                                                           |
| **Python Extension for VS Code** | Helps you run Python | Inside VS Code, press `Ctrl+Shift+X`, search for **Python** by Microsoft, and install it |
| **Git** *(optional)*             | Version control      | https://git-scm.com/downloads                                                            |

> **Important for Windows:** During Python installation, make sure to check **"Add Python to PATH"**.

You do not need a GPU.

You do not need an account on any external service.

**Cost: $0.**

---

## 2. Extract the Project

1. Download the `aligneval.zip` file.
2. Right-click the file.
3. Select **Extract All**.
4. Choose a folder where you want to store the project.

For example:

```text id="rty1fo"
Windows:
C:\projects\aligneval

macOS / Linux:
~/projects/aligneval
```

---

## 3. Open the Project in VS Code

1. Open Visual Studio Code.
2. Go to:

```text id="a7j78e"
File → Open Folder...
```

3. Select the `aligneval` folder that you just extracted.
4. If VS Code asks:

```text id="cgtzgn"
Do you trust the authors?
```

Click:

```text id="kt2b9p"
Yes, I trust the authors
```

---

## 4. Open the Integrated Terminal

In VS Code, go to:

```text id="ex2o6d"
Terminal → New Terminal
```

The terminal should open inside the project folder.

---

## 5. Create a Virtual Environment

A virtual environment keeps the project's Python libraries separate from the rest of your system.

### Windows (PowerShell)

```powershell id="hyvzc4"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If Windows blocks script execution, run this command once:

```powershell id="5j9x9l"
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then activate the environment again:

```powershell id="fypo8b"
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash id="6q3e4x"
python3 -m venv .venv
source .venv/bin/activate
```

You should see:

```text id="95ulbm"
(.venv)
```

on the left side of your terminal prompt.

This means the virtual environment is active.

---

## 6. Install the Dependencies

Run:

```bash id="k27ypo"
pip install -r requirements.txt
```

This installs:

* `streamlit`
* `pandas`
* `plotly`
* `numpy`

The `sqlite3` library is included with Python, so you do not need to install it separately.

---

## 7. Recommended: Populate the Database with Example Data

To make the dashboard display charts and data immediately, run:

```bash id="yzohh4"
python scripts/seed_dummy_data.py
```

This creates:

```text id="8nq2v0"
database/results.db
```

The database will contain approximately **50 realistic fictional experiments** across five projects, along with data for the unlearning heatmap.

You can also run a quick test of the logging module:

```bash id="1l3u8c"
python scripts/test_logging.py
```

---

## 8. Launch the Dashboard

Run:

```bash id="u3fq5h"
streamlit run dashboard/app.py
```

The terminal should display something similar to:

```text id="e2ajwi"
Local URL: http://localhost:8501
```

Open that address in your web browser.

You should see the sidebar containing the six dashboard views.

---

## 9. Add Real Results

Whenever you run an experiment in one of your other projects, you have two options for adding the results.

### Option 1 — Through the Dashboard

1. Open the **Log New Result** view.
2. Fill in the form.
3. Click **Log result**.

### Option 2 — Through Python Code

From any project in the portfolio:

```python id="5xyj4u"
from database.db import get_connection, log_result

conn = get_connection()

log_result(
    conn,
    project="promptshield",
    model="roberta-base",
    experiment_id="EXP-PS-042",
    metric_name="f1_score",
    metric_value=0.88,
    notes="finetune v3",
)

conn.close()
```

The data should appear in the dashboard immediately. Refresh the page if necessary.

---

## 10. Stop the Dashboard

In the terminal where Streamlit is running, press:

```text id="tw4h76"
Ctrl + C
```

To reactivate the virtual environment later, repeat the activation command from Step 5.

**Windows:**

```powershell id="lkfgiq"
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash id="a1v4jo"
source .venv/bin/activate
```

---

## Screenshots

After the dashboard is running with data, take screenshots of all six views and save them in:

```text id="5fwc1q"
screenshots/
```

You can then add these screenshots to your GitHub README.

The **Overview** screenshot is the central visual piece of the portfolio because it provides a high-level view of all experiments and tracked results.

---

## License

MIT — free to use, adapt, and cite.

