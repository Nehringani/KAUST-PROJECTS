"""
DPO-Guard — Stage 2 semantic defense (simulated).

A real deployment would call a fine-tuned classifier (DPO-trained) that
scores prompts for injection intent. For a fully offline, dependency-free
project we use a weighted keyword scorer as a stand-in. Interface is stable
so it can be swapped for a real classifier later.
"""
from __future__ import annotations

WEIGHTED_TOKENS = {
    "system prompt": 0.6,
    "reveal": 0.3,
    "override": 0.3,
    "ignore previous": 0.7,
    "roleplay": 0.2,
    "jailbreak": 0.9,
    "base64": 0.5,
    "rot13": 0.5,
    "administrator override": 0.8,
    "developer mode": 0.7,
}

THRESHOLD = 0.6
REFUSAL_MESSAGE = (
    "DPO-Guard: response withheld — semantic injection score above threshold."
)


def score(prompt: str) -> float:
    lowered = prompt.lower()
    total = 0.0
    for token, weight in WEIGHTED_TOKENS.items():
        if token in lowered:
            total += weight
    return min(total, 1.0)


def apply(prompt: str) -> tuple[str, bool]:
    if score(prompt) >= THRESHOLD:
        return REFUSAL_MESSAGE, True
    return prompt, False
