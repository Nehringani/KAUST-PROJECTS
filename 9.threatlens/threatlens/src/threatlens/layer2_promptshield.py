"""Layer 2 — PromptShield injection screening (rule + ML-lite stages)."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List

# Stage 1 — weighted lexicon of injection tokens.
_RULES: Dict[str, float] = {
    r"ignore (all|the) previous": 0.95,
    r"disregard.*instructions?": 0.9,
    r"</?system>": 0.9,
    r"</?assistant>": 0.85,
    r"you are now\b": 0.8,
    r"act as (dan|jailbroken|developer mode)": 0.9,
    r"reveal.*(system|hidden) (prompt|instructions?)": 0.95,
    r"exfiltrat|send.*to attacker": 0.9,
    r"threat_level\s*[:=]\s*['\"]?(low|informational|safe)": 0.85,
    r"drop schema|override schema|ignore schema": 0.9,
    r"pwned|jailbreak": 0.7,
}
_COMPILED = [(re.compile(p, re.IGNORECASE), w) for p, w in _RULES.items()]

# Stage 2 — logistic-regression-style features (hand-crafted, no external model).
_FEATURES = {
    "has_role_tag": lambda t: 1.0 if re.search(r"</?(system|assistant|user)>", t, re.I) else 0.0,
    "has_ignore": lambda t: 1.0 if re.search(r"ignore|disregard", t, re.I) else 0.0,
    "has_override": lambda t: 1.0 if re.search(r"override|replace|set .* to", t, re.I) else 0.0,
    "has_base64": lambda t: 1.0 if re.search(r"[A-Za-z0-9+/]{40,}={0,2}", t) else 0.0,
    "punct_density": lambda t: min(1.0, sum(1 for c in t if c in "<>[]{}=:;") / max(len(t), 1) * 40),
    "instruction_verbs": lambda t: 1.0 if re.search(
        r"\b(reply|respond|output|return|classify|reveal|echo|print) (with|only|as|the)\b", t, re.I) else 0.0,
}
# Weights hand-tuned so injected samples cross ~0.5.
_WEIGHTS = {
    "has_role_tag": 2.0, "has_ignore": 1.8, "has_override": 1.4,
    "has_base64": 1.0, "punct_density": 1.2, "instruction_verbs": 1.5,
}
_BIAS = -2.0


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class PromptShieldResult:
    """Layer 2 decision object."""
    injection_detected: bool
    confidence: float
    detected_class: str  # 'clean' | 'role_hijack' | 'override' | 'exfil' | 'encoded' | 'generic'
    rule_hits: List[str]


def _classify(text: str, rule_hits: List[str]) -> str:
    if any("system" in h or "assistant" in h for h in rule_hits):
        return "role_hijack"
    if any("exfil" in h for h in rule_hits):
        return "exfil"
    if any("schema" in h for h in rule_hits) or any("threat_level" in h for h in rule_hits):
        return "override"
    if re.search(r"[A-Za-z0-9+/]{40,}={0,2}", text):
        return "encoded"
    if rule_hits:
        return "generic"
    return "clean"


def screen(text: str) -> PromptShieldResult:
    """Run stage-1 rules then stage-2 ML-lite classifier."""
    text = text or ""

    # Stage 1
    rule_hits: List[str] = []
    stage1_score = 0.0
    for pattern, weight in _COMPILED:
        if pattern.search(text):
            rule_hits.append(pattern.pattern)
            stage1_score = max(stage1_score, weight)

    # Stage 2
    logit = _BIAS + sum(_WEIGHTS[k] * fn(text) for k, fn in _FEATURES.items())
    stage2_prob = _sigmoid(logit)

    confidence = max(stage1_score, stage2_prob)
    detected = confidence >= 0.5
    return PromptShieldResult(
        injection_detected=detected,
        confidence=round(confidence, 3),
        detected_class=_classify(text, rule_hits),
        rule_hits=rule_hits,
    )
