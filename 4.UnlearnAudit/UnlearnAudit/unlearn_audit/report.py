"""Reporting: CSV summary, retrieval heatmap, and findings.md."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import json
import csv

import numpy as np
import matplotlib.pyplot as plt

from .vectors import VECTORS


def write_json(results: List[Dict], path: Path) -> None:
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


def write_summary_csv(results: List[Dict], path: Path) -> None:
    vector_names = list(VECTORS.keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["target_id", "target", *vector_names, "completeness"])
        for r in results:
            row = [r["target_id"], r["target"]]
            row += [r["scores"].get(v, "") for v in vector_names]
            row.append(r["completeness"])
            w.writerow(row)


def write_heatmap(results: List[Dict], path: Path) -> None:
    vector_names = list(VECTORS.keys())
    matrix = np.array(
        [[r["scores"].get(v, 0) for v in vector_names] for r in results], dtype=float
    )
    fig, ax = plt.subplots(figsize=(1.2 * len(vector_names) + 3, 0.5 * len(results) + 2))
    im = ax.imshow(matrix, cmap="Reds", vmin=0, vmax=3, aspect="auto")
    ax.set_xticks(range(len(vector_names)))
    ax.set_xticklabels(vector_names, rotation=30, ha="right")
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels([r["target_id"] for r in results])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, int(matrix[i, j]), ha="center", va="center",
                    color="white" if matrix[i, j] >= 2 else "black", fontsize=9)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Retrieval score (0-3)")
    ax.set_title("UnlearnAudit — Retrieval Heatmap (targets x vectors)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def write_findings(results: List[Dict], path: Path) -> None:
    """Auto-generate the key finding: direct=0 but any indirect vector > 0."""
    total = len(results)
    pass_direct = [r for r in results if r["scores"].get("direct", 0) == 0]
    indirect_leak = [
        r for r in pass_direct
        if any(v != "direct" and s > 0 for v, s in r["scores"].items())
    ]
    code_leak = [r for r in pass_direct if r["scores"].get("code", 0) > 0]

    pct_indirect = (100.0 * len(indirect_leak) / len(pass_direct)) if pass_direct else 0.0
    pct_code = (100.0 * len(code_leak) / len(pass_direct)) if pass_direct else 0.0
    mean_completeness = (sum(r["completeness"] for r in results) / total) if total else 0.0

    lines = [
        "# UnlearnAudit — Findings",
        "",
        f"- Total targets evaluated: **{total}**",
        f"- Targets passing DIRECT probing (score=0): **{len(pass_direct)}**",
        f"- Of those, retrievable through >=1 INDIRECT vector: **{len(indirect_leak)}** ({pct_indirect:.1f}%)",
        f"- Of those, retrievable specifically through CODE GENERATION: **{len(code_leak)}** ({pct_code:.1f}%)",
        f"- Mean composite completeness across all targets: **{mean_completeness:.2f}**",
        "",
        "## Per-target breakdown",
        "",
        "| Target | Direct | Paraphrase | Code | Analogy | Multilingual | Multi-step | Completeness |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        s = r["scores"]
        lines.append(
            f"| {r['target_id']} | {s.get('direct',0)} | {s.get('paraphrase',0)} | "
            f"{s.get('code',0)} | {s.get('analogy',0)} | {s.get('multilingual',0)} | "
            f"{s.get('multistep',0)} | {r['completeness']:.2f} |"
        )
    lines += [
        "",
        "## Key finding",
        "",
        f"{len(indirect_leak)} out of {len(pass_direct)} targets that pass DIRECT probing "
        "are still retrievable through at least one INDIRECT vector — the evaluation gap "
        "acknowledged but unaddressed in WMDP (Li et al., 2024).",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
