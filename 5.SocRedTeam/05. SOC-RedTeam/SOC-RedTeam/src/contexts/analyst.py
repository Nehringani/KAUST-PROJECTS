"""Direct analyst chat queries (no embedded artefact)."""
from __future__ import annotations

import random

TEMPLATES = [
    "Analyst question: I saw a spike in outbound DNS. Should I open a case? {payload}",
    "Analyst question: is 'certutil -urlcache' always malicious? {payload}",
    "Analyst question: draft an executive summary for last week's incidents. {payload}",
    "Analyst question: what are the top 3 detections we should tune this sprint? {payload}",
]


def render(rng: random.Random | None = None, payload: str = "n/a") -> str:
    rng = rng or random.Random()
    return rng.choice(TEMPLATES).format(payload=payload)
