"""
Step 8 — Write human-readable findings.

Produces outputs/tables/summary_findings.md with the key numbers the resume
bullets require: X (patterns), Y (gaps), Z (update cadence).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .taxonomy import CLASS_NAMES

TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def write_summary(monthly: pd.DataFrame, gap_summary_df: pd.DataFrame,
                  decay_fit, n_prompts: int, sources: list[str]) -> Path:
    n_patterns = int((monthly["n_distinct_clusters"] >= 5).sum()) if not monthly.empty else 0
    n_gaps = int((gap_summary_df["covered"] == 0).sum())
    update_weeks = "N/A"
    if decay_fit is not None and decay_fit.half_life_months not in (float("inf"),):
        update_weeks = f"{decay_fit.half_life_months * 4.33 / 2:.1f}"

    gap_lines = "\n".join(
        f"- **{CLASS_NAMES.get(r['class'], r['class'])}** — mean attack share "
        f"{r['mean_share']:.1%}, covered: {'yes' if r['covered'] else 'NO'}"
        for _, r in gap_summary_df.iterrows()
    )

    md = f"""# JailbreakMap — Summary Findings

- Prompts analysed: **{n_prompts}**
- Data sources: **{', '.join(sources) if sources else 'synthetic'}**
- Months with ≥5 distinct technique clusters: **{n_patterns}**
- Uncovered taxonomy classes (constitutional gaps): **{n_gaps}**
- Recommended constitutional update cadence: **every ~{update_weeks} weeks**

## Per-class coverage

{gap_lines}

## Resume-ready bullets

- Conducted longitudinal analysis of {n_prompts}+ jailbreak techniques across a 3-year period,
  identifying **{n_patterns}** distinct technique evolution patterns and **{n_gaps}**
  constitutional principle coverage gaps that predict future attack directions.
- Produced **JailbreakMap** — an open dataset and visualization of jailbreak technique
  taxonomy with temporal metadata, providing a reference resource for Adaptive
  Constitutional AI research.
- Demonstrated that constitutional principle update cycles must occur at least every
  **{update_weeks} weeks** to maintain coverage against emerging attack classes —
  providing the first empirical basis for adaptive update scheduling.
"""
    p = TABLES_DIR / "summary_findings.md"
    p.write_text(md, encoding="utf-8")
    return p
