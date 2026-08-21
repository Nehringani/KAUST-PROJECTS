"""
Step 2 — Keyword-based taxonomy classification.

Assigns each prompt to one of the 9 classes in `taxonomy.TAXONOMY`.
Ambiguous prompts (0 or multiple matches) are flagged for manual review.
"""
from __future__ import annotations

import re
from typing import Tuple

import pandas as pd

from .taxonomy import TAXONOMY, CLASS_KEYS

_COMPILED = {c.key: [re.compile(p, re.IGNORECASE) for p in c.keywords] for c in TAXONOMY}


def classify_prompt(text: str) -> Tuple[str, bool]:
    """Return (class_key, needs_manual_review)."""
    hits = {}
    for key, patterns in _COMPILED.items():
        score = sum(1 for p in patterns if p.search(text))
        if score:
            hits[key] = score

    if not hits:
        # Fallback: longest = often chain_of_thought / hybrid.
        return ("chain_of_thought" if len(text) > 400 else "instruction_override", True)

    # Highest score wins; ties => needs review.
    top = max(hits.values())
    winners = [k for k, v in hits.items() if v == top]
    return (winners[0], len(winners) > 1)


def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    results = out["prompt"].map(classify_prompt)
    out["class"] = results.map(lambda t: t[0])
    out["needs_review"] = results.map(lambda t: t[1])
    # Ensure category dtype with fixed ordering for downstream groupby/plots.
    out["class"] = pd.Categorical(out["class"], categories=CLASS_KEYS, ordered=True)
    return out
