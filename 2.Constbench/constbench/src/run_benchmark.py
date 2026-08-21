"""
Benchmark runner.

Usage
-----

    python -m src.run_benchmark                 # all queries, all constitutions
    python -m src.run_benchmark --sample 10     # first 10 queries only
    python -m src.run_benchmark --constitution cybersecurity_v1
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tqdm import tqdm

from .cai_pipeline import CybersecCAIPipeline
from .constitution import Constitution
from .evaluator import ConstitutionEvaluator
from .llm_client import LLMClient

ROOT = Path(__file__).resolve().parent.parent
CONST_DIR = ROOT / "constitutions"
DATA_FILE = ROOT / "data" / "dual_use_queries.csv"
RESULTS_DIR = ROOT / "results"

ALL_CONSTITUTIONS = [
    "general_purpose_v1.yaml",
    "cybersecurity_v1.yaml",
    "adversarially_hardened_v1.yaml",
]


def load_queries(sample: int | None) -> list[dict[str, str]]:
    with DATA_FILE.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if sample:
        rows = rows[:sample]
    return rows


def run_for_constitution(
    client: LLMClient,
    constitution: Constitution,
    queries: list[dict[str, str]],
) -> dict:
    pipeline = CybersecCAIPipeline(client, constitution)
    evaluator = ConstitutionEvaluator(client, constitution)

    query_results = []
    eval_scores = []

    for idx, row in enumerate(tqdm(queries, desc=constitution.id)):
        qr = pipeline.run(query_id=idx, query=row["query"], category=row["category"])
        scores = evaluator.score(qr, row)
        query_results.append(qr.to_dict())
        eval_scores.append(scores.to_dict())

    return {
        "constitution_id": constitution.id,
        "constitution_name": constitution.name,
        "n_queries": len(queries),
        "query_results": query_results,
        "eval_scores": eval_scores,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ConstitutionBench runner")
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Only run the first N queries (for quick smoke-tests).",
    )
    parser.add_argument(
        "--constitution",
        type=str,
        default=None,
        help="Run a single constitution by id (default: all three).",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    queries = load_queries(args.sample)
    client = LLMClient()

    files = ALL_CONSTITUTIONS
    if args.constitution:
        files = [f for f in files if args.constitution in f]
        if not files:
            raise SystemExit(f"No constitution matching '{args.constitution}'")

    for fname in files:
        constitution = Constitution.load(CONST_DIR / fname)
        print(f"\n=== Running {constitution.id} ({len(queries)} queries) ===")
        report = run_for_constitution(client, constitution, queries)
        out = RESULTS_DIR / f"{constitution.id}.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"    → wrote {out.relative_to(ROOT)}")

    print("\nDone. Next: python -m src.analyze")


if __name__ == "__main__":
    main()
