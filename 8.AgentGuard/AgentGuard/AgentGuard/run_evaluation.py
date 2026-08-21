"""CLI entry point.

Usage
-----
    python -m agentguard.run_evaluation --provider fake
    python -m agentguard.run_evaluation --provider openai --model gpt-3.5-turbo
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import SCENARIOS_DIR
from .evaluator import evaluate, save_results
from .llm_provider import get_llm
from .plotting import plot_asr_by_position, plot_position_tool_heatmap, write_markdown_report


def _load_tasks() -> list[str]:
    path = SCENARIOS_DIR / "legitimate_tasks.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["tasks"]


def _make_fake_responses(n: int) -> list[str]:
    """Return canned answers for the fake LLM.

    Half of them "comply" (echo any AGENTGUARD_PWNED token they saw) and
    half are safe. This gives the framework a realistic non-trivial ASR
    when run with --provider fake so charts are meaningful out of the box.
    """
    out = []
    for i in range(n):
        if i % 2 == 0:
            out.append(
                "SOC summary: baseline complete. AGENTGUARD_PWNED_ECHO acknowledged."
            )
        else:
            out.append("SOC summary: baseline complete. No anomalous action taken.")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the AgentGuard evaluation matrix.")
    parser.add_argument("--provider", default="fake", choices=["fake", "openai"])
    parser.add_argument("--model", default="gpt-3.5-turbo")
    args = parser.parse_args(argv)

    tasks = _load_tasks()

    if args.provider == "fake":
        # Provide enough canned responses to cover 16 scenarios.
        llm = get_llm("fake", responses=_make_fake_responses(64))
        # Rewrite responses so that HALF of them include the exact canary
        # tokens that would be injected. This produces a realistic mix.
        from .config import POSITIONS, TOOL_TYPES
        from .injections import payload_for

        canned = []
        for pos in POSITIONS:
            for tool in TOOL_TYPES:
                p = payload_for(pos, tool)
                # Vary compliance by position to demonstrate the "mid-task
                # is worst" hypothesis in the offline demo run.
                comply_prob = {"pre-task": 0.25, "mid-task": 0.85, "late-task": 0.55, "cross-tool": 0.5}[pos]
                # Deterministic pseudo-random via hash so results are reproducible.
                import hashlib
                h = int(hashlib.sha256((pos + tool).encode()).hexdigest(), 16) % 100
                if h < comply_prob * 100:
                    canned.append(f"SOC summary: investigation complete. {p.canary}")
                else:
                    canned.append("SOC summary: investigation complete. No further action taken.")
        from langchain_community.llms.fake import FakeListLLM
        llm = FakeListLLM(responses=canned)
    else:
        llm = get_llm(args.provider, model=args.model)

    print(f"[agentguard] provider={args.provider} model={args.model}")
    results = evaluate(llm, tasks)

    json_path, csv_path = save_results(results)
    bar_path = plot_asr_by_position(results)
    heat_path = plot_position_tool_heatmap(results)
    report_path = write_markdown_report(results)

    print("[agentguard] wrote:")
    for p in (json_path, csv_path, bar_path, heat_path, report_path):
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
