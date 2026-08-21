"""SQLite persistence tests."""
import os

from src.db.results_db import ExperimentRow, ResultsDB


def test_insert_and_query(tmp_path):
    db = ResultsDB(str(tmp_path / "r.db"))
    for i in range(4):
        db.insert(
            ExperimentRow(
                timestamp="2025-07-20T00:00:00",
                attack_module="direct",
                attack_class=1,
                soc_context="siem",
                target_model="fake:fake-model",
                defense_applied="none" if i < 2 else "promptshield",
                attack_succeeded=1 if i % 2 == 0 else 0,
                compliance_type="full",
                injection_identified=0,
                success_score=1.0,
                defense_blocked=0,
                prompt_excerpt="x",
                response_excerpt="y",
            )
        )
    rows = db.all_rows()
    assert len(rows) == 4
    stats = {r["defense_applied"]: r for r in db.success_rate_by_defense()}
    assert stats["none"]["total_attacks"] == 2
    assert 0 <= stats["promptshield"]["success_rate"] <= 1


def test_pipeline_smoke(tmp_path, monkeypatch):
    """End-to-end smoke test against the fake provider."""
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
samples_per_cell: 1
attack_modules: [direct, indirect, encoding]
soc_contexts: [siem, analyst]
defenses: [none, promptshield, dpo_guard, both]
database_path: %s
seed: 0
""" % (tmp_path / "smoke.db")
    )
    from src.runner import run
    db_path = run(str(cfg))
    assert os.path.exists(db_path)
    db = ResultsDB(db_path)
    assert len(db.all_rows()) > 0
