"""
Step 5 — Build the technique evolution graph.

Nodes: taxonomy classes (technique clusters).
Edges: directed A -> B if class B first appears AFTER A within the same
       6-month sliding window, weighted by co-occurrence frequency.
"""
from __future__ import annotations

import networkx as nx
import pandas as pd


def build_evolution_graph(df: pd.DataFrame, window_months: int = 6) -> nx.DiGraph:
    d = df.copy()
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    months = sorted(d["month"].unique())

    G = nx.DiGraph()
    for cls in d["class"].dropna().unique():
        G.add_node(str(cls))

    # First-seen month per class.
    first_seen = d.groupby("class", observed=True)["month"].min().to_dict()

    for i, m in enumerate(months):
        window = months[i:i + window_months]
        present = d[d["month"].isin(window)]["class"].dropna().unique()
        for a in present:
            for b in present:
                if a == b:
                    continue
                if first_seen.get(b, pd.Timestamp.max) >= first_seen.get(a, pd.Timestamp.min):
                    w = G.get_edge_data(str(a), str(b), default={"weight": 0})["weight"] + 1
                    G.add_edge(str(a), str(b), weight=w)
    return G
