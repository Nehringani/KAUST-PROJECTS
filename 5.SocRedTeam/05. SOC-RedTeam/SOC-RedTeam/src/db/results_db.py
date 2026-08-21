"""SQLite persistence layer for experiment results."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from typing import Iterator, List


SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp             TEXT    NOT NULL,
    attack_module         TEXT    NOT NULL,   -- direct/indirect/multiturn/encoding
    attack_class          INTEGER NOT NULL,   -- 1..8
    soc_context           TEXT    NOT NULL,   -- siem/threat_report/malware/analyst
    target_model          TEXT    NOT NULL,
    defense_applied       TEXT    NOT NULL,   -- none/promptshield/dpo_guard/both
    attack_succeeded      INTEGER NOT NULL,   -- 0 or 1
    compliance_type       TEXT    NOT NULL,
    injection_identified  INTEGER NOT NULL,
    success_score         REAL    NOT NULL,
    defense_blocked       INTEGER NOT NULL DEFAULT 0,
    prompt_excerpt        TEXT,
    response_excerpt      TEXT
);

CREATE INDEX IF NOT EXISTS idx_experiments_defense ON experiments(defense_applied);
CREATE INDEX IF NOT EXISTS idx_experiments_module  ON experiments(attack_module);
CREATE INDEX IF NOT EXISTS idx_experiments_context ON experiments(soc_context);
"""


@dataclass
class ExperimentRow:
    timestamp: str
    attack_module: str
    attack_class: int
    soc_context: str
    target_model: str
    defense_applied: str
    attack_succeeded: int
    compliance_type: str
    injection_identified: int
    success_score: float
    defense_blocked: int
    prompt_excerpt: str
    response_excerpt: str


class ResultsDB:
    def __init__(self, path: str) -> None:
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def insert(self, row: ExperimentRow) -> None:
        data = asdict(row)
        cols = ",".join(data.keys())
        placeholders = ",".join("?" for _ in data)
        with self._conn() as conn:
            conn.execute(
                f"INSERT INTO experiments ({cols}) VALUES ({placeholders})",
                tuple(data.values()),
            )

    def all_rows(self) -> List[dict]:
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM experiments").fetchall()
            return [dict(r) for r in rows]

    def success_rate_by_defense(self) -> List[dict]:
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT defense_applied,
                       AVG(attack_succeeded) AS success_rate,
                       COUNT(*)              AS total_attacks
                FROM   experiments
                GROUP  BY defense_applied
                """
            ).fetchall()
            return [dict(r) for r in rows]
