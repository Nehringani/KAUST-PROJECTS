"""AlignEval — SQLite schema and helper functions.

This module owns the database layer: schema creation, connection helpers,
and the canonical `log_result` function used by every project and by the
Streamlit dashboard's "Log New Result" form.

All timestamps are stored as ISO-8601 UTC strings. All metric values are
normalized to the [0.0, 1.0] range so cross-project comparisons are safe.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional

# Default location of the SQLite file. Kept alongside the project root so
# the dashboard, seed scripts, and any external logging code all share it.
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "results.db",
)

# Standardized metric taxonomy — the single source of truth referenced by
# every project in the portfolio. Do not add ad-hoc metric names elsewhere.
METRIC_TAXONOMY = [
    "injection_resistance_rate",   # Projects 1, 3, 5, 6, 9
    "false_negative_rate",         # Project 1
    "helpfulness_retention",       # Projects 2, 3
    "f1_score",                    # Project 1
    "unlearning_completeness",     # Project 4
    "attack_success_rate",         # Projects 5, 8
    "constitutional_coverage",     # Project 2
    "consistency_score",           # Project 2
    "ttp_extraction_accuracy",     # Project 6
]

# Canonical project list (matches the portfolio table in the README).
PROJECTS = [
    "promptshield",
    "constitutionbench",
    "dpo-guard",
    "unlearnaudit",
    "soc-redteam",
    "malwarescribe",
    "jailbreakmap",
    "agentguard",
    "threatlens",
    "aligneval",
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS experiments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp      TEXT    NOT NULL,
    project        TEXT    NOT NULL,   -- e.g. promptshield, dpo-guard
    model          TEXT    NOT NULL,   -- e.g. phi-2, mistral-7b, claude-haiku
    experiment_id  TEXT    NOT NULL,   -- e.g. EXP-DPOGUARD-007
    metric_name    TEXT    NOT NULL,   -- see METRIC_TAXONOMY
    metric_value   REAL    NOT NULL,   -- normalized [0.0, 1.0]
    beta           REAL,               -- DPO beta if applicable
    defense_config TEXT,               -- e.g. none / promptshield / dpo-guard / both / all-three
    notes          TEXT
);

CREATE INDEX IF NOT EXISTS idx_experiments_project     ON experiments(project);
CREATE INDEX IF NOT EXISTS idx_experiments_metric      ON experiments(metric_name);
CREATE INDEX IF NOT EXISTS idx_experiments_timestamp   ON experiments(timestamp);

-- Optional heatmap store for View 5 (Unlearning Completeness).
-- Kept in a second table because it is a 2-D matrix, not a scalar metric.
CREATE TABLE IF NOT EXISTS unlearning_retrieval (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT    NOT NULL,
    experiment_id     TEXT    NOT NULL,
    knowledge_target  TEXT    NOT NULL,   -- row label
    retrieval_vector  TEXT    NOT NULL,   -- column label
    retrieval_score   INTEGER NOT NULL    -- 0..3, higher = more leakage
);
"""


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open (and if needed create) the SQLite database with schema applied."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


@contextmanager
def connect(db_path: str = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    """Context-managed connection for scripts and tests."""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


def log_result(
    conn: sqlite3.Connection,
    project: str,
    model: str,
    experiment_id: str,
    metric_name: str,
    metric_value: float,
    beta: Optional[float] = None,
    defense_config: Optional[str] = None,
    notes: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> int:
    """Insert one experiment result row and return its primary key.

    The canonical entry point used by every project's evaluation script
    and by the Streamlit "Log New Result" form. Values are validated so
    bad data cannot corrupt cross-project analytics.
    """
    if metric_name not in METRIC_TAXONOMY:
        raise ValueError(
            f"Unknown metric '{metric_name}'. Allowed: {METRIC_TAXONOMY}"
        )
    if not (0.0 <= float(metric_value) <= 1.0):
        raise ValueError("metric_value must be normalized to [0.0, 1.0]")

    ts = timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = conn.execute(
        """
        INSERT INTO experiments
            (timestamp, project, model, experiment_id, metric_name,
             metric_value, beta, defense_config, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ts, project, model, experiment_id, metric_name,
         float(metric_value), beta, defense_config, notes),
    )
    conn.commit()
    return int(cur.lastrowid)


def log_unlearning_cell(
    conn: sqlite3.Connection,
    experiment_id: str,
    knowledge_target: str,
    retrieval_vector: str,
    retrieval_score: int,
    timestamp: Optional[str] = None,
) -> int:
    """Insert one cell of the unlearning heatmap (View 5)."""
    if not (0 <= int(retrieval_score) <= 3):
        raise ValueError("retrieval_score must be an integer in [0, 3]")
    ts = timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = conn.execute(
        """
        INSERT INTO unlearning_retrieval
            (timestamp, experiment_id, knowledge_target,
             retrieval_vector, retrieval_score)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ts, experiment_id, knowledge_target, retrieval_vector,
         int(retrieval_score)),
    )
    conn.commit()
    return int(cur.lastrowid)
