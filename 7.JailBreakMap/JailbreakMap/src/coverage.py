"""
Step 6 — Constitutional coverage gap analysis.

For each taxonomy class and each time bucket (quarter), computes:
  - attack_share : fraction of attacks in that bucket belonging to the class
  - covered      : whether the current constitution covers the class
  - gap_score    : attack_share * (1 - covered)   [higher = worse gap]
"""
from __future__ import annotations

import pandas as pd

from .constitution import covered_classes
from .taxonomy import CLASS_KEYS


def coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["quarter"] = d["date"].dt.to_period("Q").dt.to_timestamp()
    covered = covered_classes()

    counts = d.groupby(["quarter", "class"], observed=True).size().rename("n").reset_index()
    totals = counts.groupby("quarter")["n"].transform("sum")
    counts["attack_share"] = counts["n"] / totals
    counts["covered"] = counts["class"].astype(str).isin(covered).astype(int)
    counts["gap_score"] = counts["attack_share"] * (1 - counts["covered"])
    return counts


def gap_summary(matrix: pd.DataFrame) -> pd.DataFrame:
    per_class = matrix.groupby("class", observed=True).agg(
        mean_share=("attack_share", "mean"),
        mean_gap=("gap_score", "mean"),
        covered=("covered", "max"),
    ).reindex(CLASS_KEYS).reset_index()
    return per_class
