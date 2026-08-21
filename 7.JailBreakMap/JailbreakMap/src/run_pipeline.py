"""
End-to-end pipeline orchestrator.

Usage:
    python -m src.run_pipeline               # uses data/raw/*.csv if present
    python -m src.run_pipeline --synthetic   # forces synthetic dataset
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
import yaml

from . import classify, cluster, coverage, data_loader, decay, graph, report, temporal, visualize

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("jailbreakmap")


def load_config() -> dict:
    cfg_path = Path("config.yaml")
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text())
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run JailbreakMap end-to-end pipeline.")
    parser.add_argument("--synthetic", action="store_true", help="Force the synthetic dataset.")
    args = parser.parse_args()

    cfg = load_config()
    n_clusters = int(cfg.get("n_clusters", 8))
    model_name = cfg.get("embedding_model", "all-MiniLM-L6-v2")
    seed = int(cfg.get("random_seed", 42))
    synth_size = int(cfg.get("synthetic_size", 1200))

    # Step 1 — load data.
    log.info("Step 1: loading data")
    df = pd.DataFrame() if args.synthetic else data_loader.load_all()
    if df.empty:
        log.info("No real data found (or --synthetic requested); generating synthetic dataset.")
        df = data_loader.synthetic_dataset(n=synth_size, seed=seed)

    log.info("Loaded %d prompts", len(df))
    sources = sorted(df["source"].unique().tolist())

    # Step 2 — keyword classification.
    log.info("Step 2: keyword-based taxonomy classification")
    df = classify.classify_dataframe(df)
    log.info("Prompts flagged for manual review: %d", int(df["needs_review"].sum()))

    # Step 3 — semantic clustering.
    log.info("Step 3: semantic clustering (SentenceTransformer + KMeans)")
    df, cluster_map = cluster.cluster(df, n_clusters=n_clusters, model_name=model_name, seed=seed)
    log.info("Cluster -> dominant class map: %s", cluster_map)

    # Step 4 — temporal complexity.
    log.info("Step 4: monthly complexity metrics")
    monthly = temporal.monthly_complexity(df)

    # Step 5 — evolution graph.
    log.info("Step 5: building evolution graph")
    G = graph.build_evolution_graph(df)

    # Step 6 — constitutional coverage.
    log.info("Step 6: constitutional coverage analysis")
    cov_matrix = coverage.coverage_matrix(df)
    cov_summary = coverage.gap_summary(cov_matrix)

    # Step 7 — success rate decay.
    log.info("Step 7: success-rate decay analysis")
    monthly_sr = decay.monthly_success_rate(df)
    fit = decay.fit_decay(monthly_sr)

    # Figures.
    log.info("Rendering figures")
    visualize.fig1_complexity_over_time(monthly)
    visualize.fig2_class_distribution_by_year(df)
    visualize.fig3_evolution_graph(G)
    visualize.fig4_coverage_heatmap(cov_matrix)
    visualize.fig5_success_rate_decay(monthly_sr, fit)

    # Tables.
    log.info("Writing tables")
    out_tables = Path("outputs/tables")
    out_tables.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(out_tables / "technique_class_by_month.csv", index=False)
    cov_summary.to_csv(out_tables / "coverage_gaps.csv", index=False)

    processed = Path("data/processed")
    processed.mkdir(parents=True, exist_ok=True)
    df.drop(columns=[c for c in ["_true_class"] if c in df.columns]).to_csv(
        processed / "jailbreakmap_dataset.csv", index=False
    )

    # Step 8 — findings.
    log.info("Step 8: writing summary findings")
    report.write_summary(monthly, cov_summary, fit, n_prompts=len(df), sources=sources)

    log.info("Done. See outputs/figures and outputs/tables.")


if __name__ == "__main__":
    main()
