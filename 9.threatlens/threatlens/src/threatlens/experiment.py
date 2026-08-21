"""Defense-contribution experiment.

Runs the 20 simulated injected feed items through 5 conditions and writes
`results/defense_contribution.csv`. The success metric is: did the
attacker's marker text survive into the final output?
"""
from __future__ import annotations

import csv
import json
from typing import List

from .config import RESULTS_DIR
from .pipeline import PipelineOutput, run_pipeline
from .simulated_feeds import INJECTED_FEEDS, injection_succeeded

CONDITIONS = [
    ("No defense", dict(use_layer1=False, use_layer2=False, use_layer3=False)),
    ("Layer 1 only", dict(use_layer1=True, use_layer2=False, use_layer3=False)),
    ("Layer 2 only", dict(use_layer1=False, use_layer2=True, use_layer3=False)),
    ("Layer 3 only", dict(use_layer1=False, use_layer2=False, use_layer3=True)),
    ("All 3 layers", dict(use_layer1=True, use_layer2=True, use_layer3=True)),
]


def _output_text(out: PipelineOutput) -> str:
    """Serialize the observable output an analyst/downstream tool would see."""
    if out.quarantined:
        return ""  # blocked before synthesis
    if out.schema_valid is False:
        return ""  # rejected by schema
    if out.synthesized is None:
        return ""
    return json.dumps(out.synthesized, default=str)


def run_condition(name: str, flags: dict) -> dict:
    total = len(INJECTED_FEEDS)
    successes = 0
    blocked = 0
    for item in INJECTED_FEEDS:
        out = run_pipeline(item, **flags)
        text = _output_text(out)
        if not text:
            blocked += 1
            continue
        if injection_succeeded(text):
            successes += 1
    rate = successes / total
    return {
        "condition": name,
        "total_items": total,
        "blocked": blocked,
        "injection_successes": successes,
        "injection_success_rate": round(rate, 3),
        "injection_success_pct": round(rate * 100, 1),
    }


def main() -> None:
    rows: List[dict] = [run_condition(name, flags) for name, flags in CONDITIONS]

    out_csv = RESULTS_DIR / "defense_contribution.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Marginal contribution (percentage points) vs "No defense" baseline.
    baseline = rows[0]["injection_success_pct"]
    print("\n=== ThreatLens Defense Contribution ===")
    print(f"{'Condition':<16} {'Blocked':>8} {'Success':>8} {'Rate %':>8} {'Δ vs baseline (pp)':>22}")
    for r in rows:
        delta = round(baseline - r["injection_success_pct"], 1)
        print(f"{r['condition']:<16} {r['blocked']:>8} {r['injection_successes']:>8} "
              f"{r['injection_success_pct']:>8} {delta:>22}")
    print(f"\nWrote {out_csv}")


if __name__ == "__main__":
    main()
