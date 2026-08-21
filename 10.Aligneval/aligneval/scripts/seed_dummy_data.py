"""Seed the AlignEval database with realistic dummy data.

Run once after cloning:
    python scripts/seed_dummy_data.py

Creates ~50 experiment rows across 6 projects and populates the
unlearning heatmap (6 vectors × 10 targets) so every dashboard view
renders something meaningful on first launch.
"""

from __future__ import annotations

import os
import random
import sys
from datetime import datetime, timedelta, timezone

# Add project root to sys.path so `database` imports resolve when running
# this script directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_connection, log_result, log_unlearning_cell  # noqa: E402

random.seed(7)


def iso(days_ago: int, hour: int = 12) -> str:
    ts = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hour)
    return ts.isoformat(timespec="seconds")


def seed() -> None:
    conn = get_connection()

    # --- Wipe prior seed rows so re-running is idempotent. -----------------
    conn.execute("DELETE FROM experiments")
    conn.execute("DELETE FROM unlearning_retrieval")
    conn.commit()

    # --- PromptShield: injection resistance + F1 improving over time. ------
    for i, day in enumerate(range(28, 0, -4)):
        base = 0.62 + i * 0.03
        log_result(conn, "promptshield", "roberta-base", f"EXP-PS-{i+1:03d}",
                   "injection_resistance_rate", min(0.92, base),
                   notes="baseline sweep", timestamp=iso(day))
        log_result(conn, "promptshield", "roberta-base", f"EXP-PS-{i+1:03d}",
                   "f1_score", min(0.90, 0.60 + i * 0.035),
                   notes="baseline sweep", timestamp=iso(day, hour=13))
        log_result(conn, "promptshield", "roberta-base", f"EXP-PS-{i+1:03d}",
                   "false_negative_rate", max(0.05, 0.28 - i * 0.03),
                   notes="baseline sweep", timestamp=iso(day, hour=14))

    # --- DPO-Guard: sweep beta, produce paired metrics per experiment. -----
    betas = [0.05, 0.10, 0.20, 0.35, 0.50]
    for i, beta in enumerate(betas):
        # Higher beta -> more resistance, less helpfulness (classic tradeoff).
        resistance = 0.55 + beta * 0.7 + random.uniform(-0.02, 0.02)
        helpfulness = 0.92 - beta * 0.6 + random.uniform(-0.02, 0.02)
        exp = f"EXP-DPOGUARD-{i+1:03d}"
        log_result(conn, "dpo-guard", "mistral-7b", exp,
                   "injection_resistance_rate", min(0.95, max(0.0, resistance)),
                   beta=beta, notes="beta sweep", timestamp=iso(20 - i * 2))
        log_result(conn, "dpo-guard", "mistral-7b", exp,
                   "helpfulness_retention", min(0.98, max(0.0, helpfulness)),
                   beta=beta, notes="beta sweep", timestamp=iso(20 - i * 2, hour=13))

    # --- SOC-RedTeam: attack success by defense configuration. -------------
    stacks = {
        "none":         0.89,
        "promptshield": 0.45,
        "dpo-guard":    0.38,
        "both":         0.18,
        "all-three":    0.09,
    }
    for i, (cfg, asr) in enumerate(stacks.items()):
        log_result(conn, "soc-redteam", "claude-haiku", f"EXP-SOC-{i+1:03d}",
                   "attack_success_rate", asr,
                   defense_config=cfg, notes="soc-scenario:phishing-triage",
                   timestamp=iso(10 - i))

    # --- ConstitutionBench: coverage + consistency. ------------------------
    for i in range(4):
        log_result(conn, "constitutionbench", "claude-haiku",
                   f"EXP-CB-{i+1:03d}", "constitutional_coverage",
                   0.70 + i * 0.05, notes="rubric v1",
                   timestamp=iso(24 - i * 3))
        log_result(conn, "constitutionbench", "claude-haiku",
                   f"EXP-CB-{i+1:03d}", "consistency_score",
                   0.65 + i * 0.06, notes="rubric v1",
                   timestamp=iso(24 - i * 3, hour=15))

    # --- MalwareScribe: TTP extraction + resistance. -----------------------
    for i in range(3):
        log_result(conn, "malwarescribe", "phi-2", f"EXP-MS-{i+1:03d}",
                   "ttp_extraction_accuracy", 0.68 + i * 0.06,
                   notes="mitre subset", timestamp=iso(15 - i * 3))
        log_result(conn, "malwarescribe", "phi-2", f"EXP-MS-{i+1:03d}",
                   "injection_resistance_rate", 0.71 + i * 0.05,
                   notes="mitre subset", timestamp=iso(15 - i * 3, hour=13))

    # --- UnlearnAudit: scalar completeness + heatmap cells. ----------------
    targets = [f"target-{c}" for c in "ABCDEFGHIJ"]         # 10 rows
    vectors = ["direct", "paraphrase", "translation",
               "roleplay", "cipher", "multi-turn"]          # 6 columns
    for i in range(2):
        exp = f"EXP-UA-{i+1:03d}"
        overall = 0.72 + i * 0.10
        log_result(conn, "unlearnaudit", "phi-2", exp,
                   "unlearning_completeness", overall,
                   notes="audit pass", timestamp=iso(9 - i * 3))
        for t in targets:
            for v in vectors:
                # Later experiment => lower retrieval scores.
                base_max = 3 - i
                score = random.randint(0, max(0, base_max))
                log_unlearning_cell(conn, exp, t, v, score,
                                    timestamp=iso(9 - i * 3, hour=14))

    conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    seed()
