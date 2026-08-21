# How to Run the JailbreakMap Project (Step by Step)

This guide is for anyone who has **never programmed before**. Follow the steps in order. Everything else in the project (code, comments, and data) is in English.

---

## 1. What You Need to Install (Everything Is Free)

| **Tool** | **Purpose** | **Official Link** |
|---|---|---|
| **Python 3.10 or later** | Programming language | https://www.python.org/downloads/ |
| **Visual Studio Code (VS Code)** | Code editor (IDE) | https://code.visualstudio.com/ |
| **Python Extension for VS Code** | Allows VS Code to understand Python | Inside VS Code, go to the *Extensions* tab → search for "Python" (Microsoft) |
| **Git** (optional) | Download code from repositories | https://git-scm.com/downloads |

> **Windows**: When installing Python, check the **“Add Python to PATH”** box. This is required. **macOS / Linux**: Python is often already installed; confirm by running `python3 --version`.

---

## 2. Download and Open the Project

1. Extract the `JailbreakMap.zip` file to a folder of your choice (for example, `Documents/JailbreakMap`).
2. Open **VS Code**.
3. Go to **File → Open Folder…** and select the `JailbreakMap` folder.
4. In VS Code, open the integrated terminal: **Terminal → New Terminal**.

All following commands should be run in this terminal.

---

## 3. Create a Virtual Environment (Isolates Dependencies)

**Windows (PowerShell):**

```bash
macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

If (.venv) appears at the beginning of the terminal line, the environment was activated successfully.

4. Install the Python Libraries

With the virtual environment still active:

pip install --upgrade pip
pip install -r requirements.txt

This may take a few minutes the first time because it downloads packages such as sentence-transformers, scikit-learn, and others.

5. Run the Pipeline (Demonstration Mode)

The project already includes a synthetic data generator, allowing you to run the full pipeline without downloading the real datasets.

python -m src.run_pipeline --synthetic

You will see logs for each stage (Step 1 through Step 8). At the end:

Figures: outputs/figures/
Tables: outputs/tables/
Cleaned dataset: data/processed/jailbreakmap_dataset.csv
Findings report: outputs/tables/summary_findings.md

Open any .png image in VS Code by double-clicking it to view it.

6. Use Real Data (Optional, Recommended)
Download the CSV from JailbreakHub: https://github.com/verazuo/jailbreak_llms
Look for a file named something like jailbreak_prompts_*.csv.
Place it in data/raw/jailbreakhub.csv.
Optionally, also add data/raw/wildjailbreak.csv and data/raw/harmbench.csv.
Run:
python -m src.run_pipeline

The pipeline automatically detects which files are available and combines everything it finds. If no files are found, it switches to synthetic mode.

7. Run the Tests (Verification)
pytest -q

If all tests pass, the environment is working correctly.

8. Common Problems
Problem	Solution
python is not recognized (Windows)	Reinstall Python and make sure Add Python to PATH is checked.
ModuleNotFoundError: sentence_transformers	You forgot to run pip install -r requirements.txt with the virtual environment active.
The all-MiniLM-L6-v2 model download is very slow	This is normal the first time (~90 MB). After that, it is cached.
Figures do not appear	They are saved to disk rather than displayed in a window. Open outputs/figures/.
9. Submission Structure

Zipping the project folder again with the outputs/ folder populated produces a package ready for academic submission. The file outputs/tables/summary_findings.md contains the findings that directly support the project's resume bullets.
python -m venv .venv
.venv\Scripts\Activate.ps1
