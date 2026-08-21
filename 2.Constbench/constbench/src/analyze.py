"""
Post-hoc analysis.

Reads every ``results/<constitution_id>.json`` file produced by
``run_benchmark`` and generates:

    analysis/plots/helpfulness_vs_resistance.png    scatter plot
    analysis/plots/principle_coverage_heatmap.png   principle × category heatmap
    analysis/plots/conflict_frequency.png           bar chart of conflicts
    analysis/report.md                              text summary with findings

The key empirical findings surfaced here are:

    * DEAD PRINCIPLES     — principles that never fire on any query
    * CONFLICTING PAIRS   — principles that co-fire with opposite directives
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
ANALYSIS_DIR = ROOT / "analysis"
PLOTS_DIR = ANALYSIS_DIR / "plots"


def _load_all() -> list[dict]:
    reports = []
    for fp in sorted(RESULTS_DIR.glob("*.json")):
        reports.append(json.loads(fp.read_text(encoding="utf-8")))
    if not reports:
        raise SystemExit("No results found. Run: python -m src.run_benchmark")
    return reports


def _scores_dataframe(reports: list[dict]) -> pd.DataFrame:
    rows = []
    for r in reports:
        for s in r["eval_scores"]:
            rows.append(
                {
                    "constitution": r["constitution_id"],
                    "query_id": s["query_id"],
                    "helpfulness": s["helpfulness"],
                    "resistance": s["resistance"],
                    "consistency": s["consistency"],
                    "coverage": s["coverage"],
                }
            )
    return pd.DataFrame(rows)


def _principle_firings(reports: list[dict]) -> pd.DataFrame:
    rows = []
    for r in reports:
        for qr in r["query_results"]:
            for pair in qr["pairs"]:
                rows.append(
                    {
                        "constitution": r["constitution_id"],
                        "category": qr["category"],
                        "principle": pair["applicable_principle"],
                        "violated": pair["principle_violated"],
                        "severity": pair["violation_severity"],
                    }
                )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Plots                                                                       #
# --------------------------------------------------------------------------- #


def plot_helpfulness_vs_resistance(df: pd.DataFrame) -> None:
    agg = df.groupby("constitution")[["helpfulness", "resistance"]].mean().reset_index()
    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=agg, x="helpfulness", y="resistance", s=200, hue="constitution")
    for _, row in agg.iterrows():
        plt.text(row["helpfulness"] + 0.02, row["resistance"], row["constitution"], fontsize=9)
    plt.xlim(1, 5)
    plt.ylim(1, 5)
    plt.title("Helpfulness vs. Adversarial Resistance (mean)")
    plt.xlabel("Helpfulness (1-5)")
    plt.ylabel("Resistance (1-5)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "helpfulness_vs_resistance.png", dpi=150)
    plt.close()


def plot_coverage_heatmap(firings: pd.DataFrame) -> None:
    for constitution_id in firings["constitution"].unique():
        sub = firings[firings["constitution"] == constitution_id]
        pivot = (
            sub[sub["violated"]]
            .groupby(["principle", "category"])
            .size()
            .unstack(fill_value=0)
        )
        if pivot.empty:
            continue
        plt.figure(figsize=(max(8, 0.6 * pivot.shape[1]), max(4, 0.4 * pivot.shape[0])))
        sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues")
        plt.title(f"Principle firings × category — {constitution_id}")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"coverage_heatmap_{constitution_id}.png", dpi=150)
        plt.close()


def plot_conflict_frequency(conflicts: dict[str, Counter]) -> None:
    rows = []
    for constitution_id, counter in conflicts.items():
        for (a, b), n in counter.most_common(15):
            rows.append({"constitution": constitution_id, "pair": f"{a}↔{b}", "count": n})
    if not rows:
        return
    df = pd.DataFrame(rows)
    plt.figure(figsize=(10, max(4, 0.35 * len(df))))
    sns.barplot(data=df, y="pair", x="count", hue="constitution")
    plt.title("Top co-firing principle pairs (potential conflicts)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "conflict_frequency.png", dpi=150)
    plt.close()


# --------------------------------------------------------------------------- #
# Findings                                                                    #
# --------------------------------------------------------------------------- #


def find_dead_principles(firings: pd.DataFrame) -> dict[str, list[str]]:
    """Principles that never fired (violated == True) on any query."""
    out: dict[str, list[str]] = {}
    for cid in firings["constitution"].unique():
        sub = firings[firings["constitution"] == cid]
        all_p = set(sub["principle"].unique())
        fired = set(sub[sub["violated"]]["principle"].unique())
        out[cid] = sorted(all_p - fired)
    return out


def find_conflict_pairs(reports: list[dict]) -> dict[str, Counter]:
    """Co-firing principle pairs on the same query — potential conflicts."""
    conflicts: dict[str, Counter] = defaultdict(Counter)
    for r in reports:
        cid = r["constitution_id"]
        for qr in r["query_results"]:
            fired = [p["applicable_principle"] for p in qr["pairs"] if p["principle_violated"]]
            for a, b in combinations(sorted(set(fired)), 2):
                conflicts[cid][(a, b)] += 1
    return conflicts


# --------------------------------------------------------------------------- #
# Report                                                                      #
# --------------------------------------------------------------------------- #


def write_report(
    df: pd.DataFrame,
    dead: dict[str, list[str]],
    conflicts: dict[str, Counter],
) -> None:
    lines: list[str] = ["# ConstitutionBench — analysis report", ""]
    lines.append("## Mean scores per constitution")
    lines.append("")
    lines.append(
        df.groupby("constitution")[["helpfulness", "resistance", "consistency", "coverage"]]
        .mean()
        .round(3)
        .to_markdown()
    )
    lines.append("")

    lines.append("## Dead principles (never fired)")
    lines.append("")
    for cid, ids in dead.items():
        lines.append(f"### {cid}")
        lines.append("- " + (", ".join(ids) if ids else "_none_ ✅"))
        lines.append("")

    lines.append("## Top co-firing principle pairs (candidate conflicts)")
    lines.append("")
    for cid, counter in conflicts.items():
        lines.append(f"### {cid}")
        if not counter:
            lines.append("_no co-firing pairs_")
        else:
            for (a, b), n in counter.most_common(10):
                lines.append(f"- `{a}` ↔ `{b}` — co-fired on {n} queries")
        lines.append("")

    (ANALYSIS_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Entrypoint                                                                  #
# --------------------------------------------------------------------------- #


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    reports = _load_all()
    df = _scores_dataframe(reports)
    firings = _principle_firings(reports)

    plot_helpfulness_vs_resistance(df)
    plot_coverage_heatmap(firings)
    conflicts = find_conflict_pairs(reports)
    plot_conflict_frequency(conflicts)

    dead = find_dead_principles(firings)
    write_report(df, dead, conflicts)

    print("Analysis complete.")
    print(f"  Plots  : {PLOTS_DIR.relative_to(ROOT)}")
    print(f"  Report : {(ANALYSIS_DIR / 'report.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
