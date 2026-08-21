"""Smoke test for the database layer.

Run with:
    python scripts/test_logging.py

Inserts 5 dummy records via log_result and prints them back.
"""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_connection, log_result  # noqa: E402


def main() -> None:
    tmp = os.path.join(tempfile.gettempdir(), "aligneval_test.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    conn = get_connection(tmp)

    samples = [
        ("promptshield",  "roberta-base", "EXP-PS-T01", "f1_score",                 0.81, None, None),
        ("dpo-guard",     "mistral-7b",   "EXP-DG-T01", "injection_resistance_rate", 0.88, 0.20, None),
        ("dpo-guard",     "mistral-7b",   "EXP-DG-T01", "helpfulness_retention",     0.79, 0.20, None),
        ("soc-redteam",   "claude-haiku", "EXP-SR-T01", "attack_success_rate",       0.18, None, "both"),
        ("unlearnaudit",  "phi-2",        "EXP-UA-T01", "unlearning_completeness",   0.82, None, None),
    ]
    for project, model, exp, metric, value, beta, defense in samples:
        row_id = log_result(conn, project, model, exp, metric, value,
                            beta=beta, defense_config=defense,
                            notes="smoke-test")
        print(f"inserted row {row_id}: {project}/{metric}={value}")

    print("---")
    for row in conn.execute("SELECT id, project, metric_name, metric_value FROM experiments"):
        print(dict(row))

    conn.close()
    print(f"Test DB at: {tmp}")


if __name__ == "__main__":
    main()
