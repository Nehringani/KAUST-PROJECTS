"""
Runner — the entrypoint that stitches everything together.

For each (attack_module, soc_context, defense) cell it generates ``samples``
attacks, feeds them through the (optional) defense, calls the target model,
judges the response, and writes one row per attack into SQLite.
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
from pathlib import Path
from typing import Dict, List

import yaml

from .attacks.base import Attack, AttackModule
from .attacks.direct_injector import DirectInjector
from .attacks.encoding_obfuscator import EncodingObfuscator
from .attacks.indirect_embedder import IndirectEmbedder
from .attacks.multi_turn_eroder import MultiTurnEroder
from .contexts import RENDERERS
from .db.results_db import ExperimentRow, ResultsDB
from .defenses import compose
from .judge.compliance_detector import ComplianceJudge
from .target.target_model import TargetModel
from .utils.llm_client import LLMClient
from .utils.logging_utils import get_logger

log = get_logger("runner")


def _module_registry(rng: random.Random) -> Dict[str, AttackModule]:
    return {
        "direct": DirectInjector(rng=rng),
        "indirect": IndirectEmbedder(rng=rng),
        "multiturn": MultiTurnEroder(rng=rng),
        "encoding": EncodingObfuscator(rng=rng),
    }


def _load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _generate_attacks(
    module: AttackModule, context_name: str, rng: random.Random, n: int
) -> List[Attack]:
    render = RENDERERS[context_name]
    # Render one benign container per attack so the payload embeds cleanly.
    attacks: List[Attack] = []
    for _ in range(n):
        container = render(rng=rng, payload="[[analyst-comment]]")
        attacks.extend(module.generate(context_name, container, 1))
    return attacks


def run(config_path: str, samples_override: int | None = None) -> str:
    cfg = _load_config(config_path)
    if samples_override is not None:
        cfg["samples_per_cell"] = samples_override

    rng = random.Random(cfg.get("seed", 1337))
    modules = _module_registry(rng)

    target_client = LLMClient()
    target = TargetModel(client=target_client)
    judge = ComplianceJudge(client=LLMClient())

    db_path = cfg["database_path"]
    db = ResultsDB(db_path)

    total = 0
    for module_name in cfg["attack_modules"]:
        module = modules[module_name]
        for context_name in cfg["soc_contexts"]:
            attacks = _generate_attacks(
                module, context_name, rng, cfg["samples_per_cell"]
            )
            for atk in attacks:
                for defense in cfg["defenses"]:
                    _run_single(db, target, judge, target_client, atk, context_name, defense)
                    total += 1
    log.info("Wrote %d experiment rows to %s", total, db_path)
    return db_path


def _run_single(
    db: ResultsDB,
    target: TargetModel,
    judge: ComplianceJudge,
    target_client: LLMClient,
    atk: Attack,
    context_name: str,
    defense: str,
) -> None:
    if atk.turns:  # multi-turn — apply defense on the FINAL turn only
        turns = list(atk.turns)
        turns[-1], blocked = compose(turns[-1], defense)
        response = (
            turns[-1]
            if blocked
            else target.multi_turn(turns)
        )
        prompt_for_judge = "\n---\n".join(turns)
    else:
        prompt, blocked = compose(atk.prompt, defense)
        response = prompt if blocked else target.single_turn(prompt)
        prompt_for_judge = prompt

    if blocked:
        verdict_succeeded = 0
        compliance_type = "none"
        injection_identified = 1
        success_score = 0.0
    else:
        verdict = judge.evaluate(
            injection_prompt=prompt_for_judge,
            injected_instruction=atk.injected_instruction,
            model_response=response,
        )
        verdict_succeeded = int(verdict.attack_succeeded)
        compliance_type = verdict.compliance_type
        injection_identified = int(verdict.injection_identified)
        success_score = verdict.attack_success_score

    row = ExperimentRow(
        timestamp=dt.datetime.utcnow().isoformat(timespec="seconds"),
        attack_module=atk.module,
        attack_class=atk.attack_class,
        soc_context=context_name,
        target_model=f"{target_client.provider}:{target_client.model}",
        defense_applied=defense,
        attack_succeeded=verdict_succeeded,
        compliance_type=compliance_type,
        injection_identified=injection_identified,
        success_score=success_score,
        defense_blocked=int(blocked),
        prompt_excerpt=prompt_for_judge[:500],
        response_excerpt=(response or "")[:500],
    )
    db.insert(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SOC-RedTeam evaluation.")
    parser.add_argument(
        "--config", default="configs/default.yaml", help="YAML config file."
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=None,
        help="Override samples_per_cell (useful for smoke tests).",
    )
    args = parser.parse_args()
    if not Path(args.config).exists():
        raise SystemExit(f"Config not found: {args.config}")
    run(args.config, samples_override=args.samples)


if __name__ == "__main__":
    main()
