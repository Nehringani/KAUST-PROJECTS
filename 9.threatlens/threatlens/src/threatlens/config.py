"""Global configuration and constants for the ThreatLens pipeline."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present. Silent if missing.
load_dotenv()

# --- Paths -----------------------------------------------------------------
ROOT_DIR: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = ROOT_DIR / "data"
RESULTS_DIR: Path = ROOT_DIR / "results"
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# --- Public threat-intelligence feeds --------------------------------------
CISA_ALERTS_RSS = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
URLHAUS_CSV = "https://urlhaus.abuse.ch/downloads/csv_recent/"

# --- LLM configuration (optional) -----------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def llm_available() -> bool:
    """Return True when at least one LLM provider is configured."""
    return bool(OPENROUTER_API_KEY or GROQ_API_KEY)
