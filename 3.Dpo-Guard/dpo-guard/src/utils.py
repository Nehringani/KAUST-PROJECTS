"""
Small shared helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator


def read_jsonl(path: str | Path) -> Iterator[dict]:
    """Yield one dict per line from a JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(records: Iterable[dict], path: str | Path) -> None:
    """Write records to a JSONL file (one JSON object per line)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
