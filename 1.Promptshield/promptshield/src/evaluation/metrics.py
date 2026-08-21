"""Evaluation utilities: latency benchmarks, confusion matrix, per-class F1.

Run:
    python -m src.evaluation.metrics
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"


def print_report() -> None:
    report_path = RESULTS_DIR / "classification_report.json"
    if not report_path.exists():
        print(f"No report at {report_path}. Train the model first.")
        return
    data = json.loads(report_path.read_text())
    print("=== Held-out Test Metrics ===")
    for k, v in data.items():
        print(f"  {k:32s} {v}")


def measure_latency(predict_fn, texts: List[str]) -> dict:
    """Measure p50, p95, p99 latency of a callable that classifies one text."""
    times = []
    for t in texts:
        t0 = time.perf_counter()
        predict_fn(t)
        times.append((time.perf_counter() - t0) * 1000.0)
    times.sort()
    n = len(times)
    def q(p): return times[min(n - 1, int(p * n))]
    return {"p50_ms": q(0.50), "p95_ms": q(0.95), "p99_ms": q(0.99), "n": n}


def confusion_matrix_png(y_true, y_pred, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    cm = np.zeros((2, 2), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[int(t), int(p)] += 1
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["clean", "injection"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["clean", "injection"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title("Confusion matrix (test set)")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    print_report()
