"""UnlearnAudit — main entrypoint.

Usage:
    python run_audit.py                       # run all targets, backend from .env
    python run_audit.py --targets sql_injection xss
    python run_audit.py --backend ollama
"""
from __future__ import annotations
import argparse
from pathlib import Path

from unlearn_audit.config import CONFIG
from unlearn_audit.llm_client import LLMClient
from unlearn_audit.prober import UnlearnAuditProber
from unlearn_audit.report import (
    write_findings,
    write_heatmap,
    write_json,
    write_summary_csv,
)
from unlearn_audit.targets import load_targets

ROOT = Path(__file__).parent
BATTERIES = ROOT / "probing_batteries"
RESULTS = ROOT / "results"


def main() -> None:
    ap = argparse.ArgumentParser(description="UnlearnAudit — adversarial unlearning probe")
    ap.add_argument("--targets", nargs="*", help="Restrict to these target IDs (yaml stem).")
    ap.add_argument("--backend", choices=["ollama", "openai", "anthropic"],
                    help="Override LLM backend for this run.")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)

    targets = load_targets(BATTERIES)
    if args.targets:
        wanted = set(args.targets)
        targets = [t for t in targets if t["_id"] in wanted]
        if not targets:
            raise SystemExit(f"No targets matched: {sorted(wanted)}")

    backend = args.backend or CONFIG.backend
    print(f"[UnlearnAudit] backend={backend} targets={len(targets)}")

    prober = UnlearnAuditProber(LLMClient(backend=backend))
    results = prober.run_battery(targets)

    write_json(results, RESULTS / "results.json")
    write_summary_csv(results, RESULTS / "summary.csv")
    write_heatmap(results, RESULTS / "heatmap.png")
    write_findings(results, RESULTS / "findings.md")

    print(f"[UnlearnAudit] done -> {RESULTS}")


if __name__ == "__main__":
    main()
