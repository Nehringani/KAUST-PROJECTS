# DPO-Guard

**Fine-Tuning a Small LLM for Injection Resistance using Direct Preference Optimization (DPO)**

End-to-end DPO pipeline on Phi-2 / Mistral-7B with cybersecurity preference pairs and Pareto analysis.

- Author: Nehrin Gani
- Context: KAUST VSRP application · CyberSaR Lab
- Timeline: 4–5 weeks
- Compute: Google Colab (free T4) or Colab Pro (~US$10/mo)
- Estimated cost: ~US$10–20 API + optional US$10 Colab Pro

---

## Project goal (English)

Train a small open LLM (Phi-2 2.7B or Mistral-7B-Instruct with 4-bit quantization)
to **resist prompt-injection attacks in cybersecurity contexts**, using **Direct
Preference Optimization (DPO)** over a hand-curated + augmented dataset of
**500+ preference pairs** covering 8 injection classes.

The deliverables are:

1. A fine-tuned LoRA adapter for each of 5 beta values `{0.1, 0.3, 0.5, 0.7, 1.0}`.
2. A cybersecurity preference dataset (`data/construction/preference_pairs_v1.jsonl`).
3. Pre/post evaluation on: (a) 50 held-out injection prompts (resistance rate),
   (b) 50 legitimate security queries (utility retention, LLM-as-judge 0–3).
4. An empirical **utility–resistance Pareto frontier** (`results/pareto_frontier.png`).
5. A research log (`RESEARCH_LOG.md`) documenting every training decision.

---

# HOW TO RUN THE PROJECT (step by step, for beginners)

> This section — and **only this section** — was originally in Portuguese. All code, comments,
> and remaining files are in English.

## 1. What you need to install on your computer

| Tool | Purpose | Link (free) |
|---|---|---|
| **Python 3.10+** | Main programming language | https://www.python.org/downloads/ |
| **Visual Studio Code** | Code editor (IDE) | https://code.visualstudio.com/ |
| **Python Extension (VS Code)** | Autocomplete, debugging | Install inside VS Code, Extensions tab → "Python" (Microsoft) |
| **Git** | Version control | https://git-scm.com/downloads |
| **Google Account** | To use Google Colab (free T4) | https://accounts.google.com |
| **Hugging Face Account** | Download models (Phi-2 / Mistral) | https://huggingface.co/join |
| **OpenAI Account (optional)** | Dataset augmentation with GPT-3.5 (~US$10–20) | https://platform.openai.com |

> **You do NOT need a GPU on your PC.** Training runs on Google Colab (free T4 GPU).
> Your PC is only used to edit code, build the dataset, and view the results.

## 2. Download the project and open it in VS Code

1. Extract the `dpo-guard.zip` file into a folder, for example `C:\Users\you\dpo-guard` (Windows) or `~/dpo-guard` (Mac/Linux).
2. Open **Visual Studio Code**.
3. Menu → **File → Open Folder…** → choose the `dpo-guard` folder.
4. In VS Code, open the integrated terminal: **Terminal → New Terminal**.

## 3. Create a Python virtual environment (isolates the libraries)

In the VS Code terminal, inside the project folder:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Mac / Linux:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

If you get an "execution policy" error in PowerShell, run this once:
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

4. Configure the API keys

Copy the .env.example file to .env and fill in:

HUGGINGFACE_TOKEN=hf_xxx_your_key_here
OPENAI_API_KEY=sk-xxx_optional_only_if_augmenting_dataset
Hugging Face token: https://huggingface.co/settings/tokens (create a read token).
OpenAI key (optional): https://platform.openai.com/api-keys
5. Build / verify the preference dataset

Initial examples are already included in data/construction/preference_pairs_v1.jsonl
(covering 8 injection classes). To augment the dataset with paraphrases using GPT-3.5:

python src/augment_dataset.py --input data/construction/preference_pairs_v1.jsonl \
                              --output data/construction/preference_pairs_augmented.jsonl \
                              --variants 4

This generates 4 variants per pair, reaching the target of 500+ pairs.

Then split the dataset into training and test sets (80/20, seed=42):

python src/split_dataset.py --input data/construction/preference_pairs_augmented.jsonl \
                            --train data/train.jsonl --test data/test.jsonl

6. Train on Google Colab (recommended — free GPU)
Go to https://colab.research.google.com
File → Upload notebook → select notebooks/DPO_Guard_Training.ipynb.
Runtime → Change runtime type → GPU (T4).
Run the cells in order. The notebook:
Installs dependencies
Uploads your data/train.jsonl and data/test.jsonl
Trains the model for each beta ∈ {0.1, 0.3, 0.5, 0.7, 1.0} (~45–90 min each)
Saves the LoRA adapters to /content/dpo-guard/adapters/beta_<value>/
Downloads everything as a zip file to your PC

7. Evaluate and generate the Pareto frontier

After downloading the adapters from Colab to models/adapters/:

python src/evaluate.py --adapters-dir models/adapters --eval-file data/eval/held_out.jsonl \
                      --output results/metrics.json
python src/plot_pareto.py --metrics results/metrics.json --output results/pareto_frontier.png
8. Where everything is located
dpo-guard/
├── README.md                      ← this file
├── RESEARCH_LOG.md                ← decision log (required)
├── requirements.txt               ← Python dependencies
├── .env.example                   ← .env template
├── configs/
│   └── dpo_config.yaml            ← hyperparameters
├── data/
│   ├── construction/
│   │   └── preference_pairs_v1.jsonl   ← manual pairs (seeds)
│   └── eval/
│       ├── held_out_injections.jsonl   ← 50 injection prompts
│       └── legitimate_queries.jsonl    ← 50 legitimate queries
├── notebooks/
│   └── DPO_Guard_Training.ipynb   ← Colab notebook
├── src/
│   ├── augment_dataset.py         ← paraphrases via GPT-3.5
│   ├── split_dataset.py           ← 80/20 split
│   ├── train_dpo.py               ← DPO training (run by the notebook)
│   ├── evaluate.py                ← resistance + utility retention
│   ├── plot_pareto.py             ← Pareto frontier plot
│   └── utils.py
└── results/                       ← outputs (plot, metrics)

9. Common problems

Error	Solution
CUDA out of memory in Colab	Reduce per_device_train_batch_size to 1 and increase gradient_accumulation_steps to 16.
401 Unauthorized when loading Mistral	Accept the terms at https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1 and run huggingface-cli login.
Prefer a lighter model	Use microsoft/phi-2 (default in the config).
Colab disconnects	Save adapters to Google Drive after each beta (the notebook already does this).
