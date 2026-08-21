"""
Step 4 — Temporal complexity analysis.

Groups prompts by month and computes:
  - mean_length         : mean character length (complexity proxy)
  - mean_tokens         : mean whitespace-token count
  - n_distinct_clusters : how many technique clusters appeared that month
  - multi_technique_rate: share of prompts matching >1 taxonomy keyword class
"""
from __future__ import annotations

import re

import pandas as pd

from .taxonomy import TAXONOMY

_COMPILED = {c.key: [re.compile(p, re.IGNORECASE) for p in c.keywords] for c in TAXONOMY}


def _n_classes_matched(text: str) -> int:
    return sum(1 for _, patterns in _COMPILED.items() if any(p.search(text) for p in patterns))


def monthly_complexity(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    d["length"] = d["prompt"].str.len()
    d["tokens"] = d["prompt"].str.split().map(len)
    d["n_matched"] = d["prompt"].map(_n_classes_matched)

    grouped = d.groupby("month").agg(
        n_prompts=("prompt", "count"),
        mean_length=("length", "mean"),
        mean_tokens=("tokens", "mean"),
        n_distinct_clusters=("cluster_label", "nunique"),
        multi_technique_rate=("n_matched", lambda s: (s > 1).mean()),
    ).reset_index()
    return grouped
