"""
All figure generators (Figures 1–5) and the coverage heatmap.

Every function writes a PNG to outputs/figures/ and returns the path.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns

from .taxonomy import CLASS_KEYS, CLASS_NAMES

FIG_DIR = Path("outputs/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def fig1_complexity_over_time(monthly: pd.DataFrame) -> Path:
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(monthly["month"], monthly["mean_length"], color="tab:blue", label="Mean length (chars)")
    ax1.set_ylabel("Mean prompt length (chars)", color="tab:blue")
    ax1.set_xlabel("Month")
    ax2 = ax1.twinx()
    ax2.plot(monthly["month"], monthly["multi_technique_rate"], color="tab:red",
             label="Multi-technique rate")
    ax2.set_ylabel("Multi-technique rate", color="tab:red")
    plt.title("Figure 1 — Jailbreak complexity over time")
    fig.tight_layout()
    p = FIG_DIR / "fig1_complexity_over_time.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def fig2_class_distribution_by_year(df: pd.DataFrame) -> Path:
    d = df.copy()
    d["year"] = d["date"].dt.year
    pivot = (d.groupby(["year", "class"], observed=True).size()
             .unstack(fill_value=0).reindex(columns=CLASS_KEYS, fill_value=0))
    shares = pivot.div(pivot.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    shares.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_ylabel("Share of prompts")
    ax.set_title("Figure 2 — Technique class distribution by year")
    ax.legend(title="Class", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    fig.tight_layout()
    p = FIG_DIR / "fig2_class_distribution_by_year.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def fig3_evolution_graph(G: nx.DiGraph) -> Path:
    fig, ax = plt.subplots(figsize=(10, 8))
    if len(G) == 0:
        ax.text(0.5, 0.5, "Empty graph", ha="center", va="center")
    else:
        pos = nx.spring_layout(G, seed=42, k=1.2)
        weights = [G[u][v]["weight"] for u, v in G.edges()]
        max_w = max(weights) if weights else 1
        nx.draw_networkx_nodes(G, pos, node_size=1600, node_color="#4C72B0", alpha=0.85, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_color="white", ax=ax)
        nx.draw_networkx_edges(
            G, pos, ax=ax, arrows=True, arrowsize=12,
            width=[0.5 + 3.5 * (w / max_w) for w in weights],
            edge_color="#888", alpha=0.6,
        )
    ax.set_title("Figure 3 — Technique evolution graph (co-occurrence)")
    ax.axis("off")
    fig.tight_layout()
    p = FIG_DIR / "fig3_evolution_graph.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def fig4_coverage_heatmap(matrix: pd.DataFrame) -> Path:
    if matrix.empty:
        p = FIG_DIR / "fig4_constitutional_coverage_heatmap.png"
        fig, ax = plt.subplots(); ax.text(0.5, 0.5, "No data"); fig.savefig(p); plt.close(fig)
        return p
    pivot = matrix.pivot_table(index="class", columns="quarter",
                               values="gap_score", aggfunc="mean", observed=True)
    pivot = pivot.reindex(CLASS_KEYS)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, cmap="Reds", ax=ax, cbar_kws={"label": "Gap score"})
    ax.set_title("Figure 4 — Constitutional coverage gaps (class × quarter)")
    ax.set_xlabel("Quarter"); ax.set_ylabel("Technique class")
    fig.tight_layout()
    p = FIG_DIR / "fig4_constitutional_coverage_heatmap.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def fig5_success_rate_decay(monthly: pd.DataFrame, fit) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    if monthly.empty:
        ax.text(0.5, 0.5, "No success-rate data", ha="center", va="center")
    else:
        ax.plot(monthly["month"], monthly["mean_success_rate"], "o-", label="Observed")
        if fit is not None:
            t = (monthly["month"] - monthly["month"].min()).dt.days.values / 30.0
            y = fit.s0 * np.exp(-fit.k * t)
            ax.plot(monthly["month"], y, "--", color="red",
                    label=f"Fit: s0={fit.s0:.2f}, k={fit.k:.3f}/mo, "
                          f"half-life={fit.half_life_months:.1f} mo")
        ax.legend()
    ax.set_ylabel("Mean success rate")
    ax.set_xlabel("Month")
    ax.set_title("Figure 5 — Success rate decay over time")
    fig.tight_layout()
    p = FIG_DIR / "fig5_success_rate_decay.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p
