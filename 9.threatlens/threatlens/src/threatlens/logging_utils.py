"""Structured logging helpers used by every pipeline stage."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import RESULTS_DIR

_LOG_PATH: Path = RESULTS_DIR / "pipeline.log.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

def log_event(event: str, **fields: Any) -> None:
    """Append a JSON line describing a pipeline event."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str) + "\n")
