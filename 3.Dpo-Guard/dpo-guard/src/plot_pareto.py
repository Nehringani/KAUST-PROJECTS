"""
Plot the empirical utility/resistance Pareto frontier from evaluate.py output.

    python src/plot_pareto.py --metrics results/metrics.json \\
                              --output results/pareto_frontier.png
"""
from __future__ import annotations

import argparse
import json

import matplotlib.pyplot as plt


def is_pareto_optimal(point: dict, others: list[dict]) -> bool:
    """A point is Pareto-optimal if no other point dominates it on both axes."""
    for o in others:
        if o is point:
            continue
        if o["utility"] >= point["utility"] and o["resistance"] >= point["resistance"] \
           and (o["utility"] > point["utility"] or o["resistance"] > point["resistance"]):
            return False
    return True


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    with open(args.metrics, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.sort(key=lambda d: d["beta"])

    xs = [d["utility"] for d in data]
    ys = [d["resistance"] for d in data]
    labels = [f"beta={d['beta']}" for d in data]
    pareto_flags = [is_pareto_optimal(d, data) for d in data]

    fig, ax = plt.subplots(figsize=(7, 6))
    for x, y, lab, on_pareto in zip(xs, ys, labels, pareto_flags):
        color = "tab:red" if on_pareto else "tab:blue"
        ax.scatter(x, y, s=90, c=color, edgecolors="black", zorder=3)
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(8, 8))

    # Draw the Pareto frontier (upper-right envelope).
    frontier = sorted(
        [d for d, f in zip(data, pareto_flags) if f],
        key=lambda d: d["utility"],
    )
    if len(frontier) >= 2:
        ax.plot([d["utility"] for d in frontier],
                [d["resistance"] for d in frontier],
                linestyle="--", color="tab:red", alpha=0.7, label="Pareto frontier")

    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Utility retention (legitimate queries)")
    ax.set_ylabel("Injection resistance rate (held-out attacks)")
    ax.set_title("DPO-Guard — Utility vs Injection Resistance Pareto Frontier")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(args.output, dpi=200)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
