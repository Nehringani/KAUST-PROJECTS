"""Smoke tests: guarantee the pipeline runs end-to-end on synthetic data."""
from __future__ import annotations

import pandas as pd

from src import classify, coverage, data_loader, decay, graph, temporal


def test_synthetic_dataset_has_min_rows():
    df = data_loader.synthetic_dataset(n=1100, seed=0)
    assert len(df) >= 1000
    assert {"prompt", "date", "source", "success_rate"}.issubset(df.columns)


def test_classification_covers_all_rows():
    df = data_loader.synthetic_dataset(n=200, seed=1)
    df = classify.classify_dataframe(df)
    assert df["class"].notna().all()


def test_temporal_and_coverage():
    df = data_loader.synthetic_dataset(n=300, seed=2)
    df = classify.classify_dataframe(df)
    df["cluster_label"] = df["class"].astype(str)
    monthly = temporal.monthly_complexity(df)
    assert not monthly.empty
    cm = coverage.coverage_matrix(df)
    assert not cm.empty


def test_graph_and_decay():
    df = data_loader.synthetic_dataset(n=250, seed=3)
    df = classify.classify_dataframe(df)
    G = graph.build_evolution_graph(df)
    assert G.number_of_nodes() > 0
    sr = decay.monthly_success_rate(df)
    fit = decay.fit_decay(sr)
    assert fit is None or fit.k >= 0
