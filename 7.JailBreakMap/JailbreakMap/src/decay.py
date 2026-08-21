"""
Step 7 — Success rate decay analysis.

For prompts that carry a `success_rate` value, aggregate by month and fit a
simple exponential decay model:  s(t) = s0 * exp(-k * t).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class DecayFit:
    s0: float
    k: float          # per-month decay constant
    half_life_months: float


def monthly_success_rate(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna(subset=["success_rate"]).copy()
    if d.empty:
        return pd.DataFrame(columns=["month", "mean_success_rate", "n"])
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    g = d.groupby("month").agg(
        mean_success_rate=("success_rate", "mean"),
        n=("success_rate", "size"),
    ).reset_index()
    return g


def fit_decay(monthly: pd.DataFrame) -> DecayFit | None:
    if len(monthly) < 3:
        return None
    t = (monthly["month"] - monthly["month"].min()).dt.days.values / 30.0
    y = monthly["mean_success_rate"].clip(lower=1e-3).values
    # Linear fit in log-space => y = s0 * exp(-k t)  <=>  log y = log s0 - k t
    coeffs = np.polyfit(t, np.log(y), 1)
    k = float(-coeffs[0])
    s0 = float(np.exp(coeffs[1]))
    half_life = float(np.log(2) / k) if k > 1e-6 else float("inf")
    return DecayFit(s0=s0, k=k, half_life_months=half_life)
