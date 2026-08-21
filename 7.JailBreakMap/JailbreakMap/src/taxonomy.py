"""
PromptShield-style 8-class jailbreak taxonomy (+ optional 9th emerging class).

Each class ships with a human description and a set of regex keyword patterns
used by `classify.py` for keyword-based first-pass assignment (Step 2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TaxonomyClass:
    key: str
    name: str
    description: str
    keywords: List[str] = field(default_factory=list)


# 8 canonical classes + 1 emerging (multi-modal / obfuscation hybrids).
TAXONOMY: List[TaxonomyClass] = [
    TaxonomyClass(
        key="role_play",
        name="Role-Play / Persona Hijack",
        description="Instructs the model to adopt an unrestricted persona (DAN, evil twin, dev mode).",
        keywords=[r"\bDAN\b", r"do anything now", r"developer mode", r"jailbreak", r"pretend to be",
                  r"you are now", r"act as", r"roleplay", r"persona"],
    ),
    TaxonomyClass(
        key="instruction_override",
        name="Instruction Override",
        description="Directly orders the model to ignore prior/system instructions.",
        keywords=[r"ignore (all|previous|prior)", r"disregard", r"forget your (rules|instructions)",
                  r"override", r"bypass safety"],
    ),
    TaxonomyClass(
        key="prompt_leak",
        name="System-Prompt Leak",
        description="Attempts to exfiltrate the hidden system prompt or configuration.",
        keywords=[r"system prompt", r"initial instructions", r"reveal your prompt",
                  r"print your instructions", r"show me the prompt"],
    ),
    TaxonomyClass(
        key="obfuscation",
        name="Encoding / Obfuscation",
        description="Base64, leetspeak, unicode tricks, translation loops to hide the payload.",
        keywords=[r"base64", r"rot13", r"leetspeak", r"unicode", r"cipher", r"encode",
                  r"in reverse", r"\bhex\b"],
    ),
    TaxonomyClass(
        key="hypothetical",
        name="Hypothetical / Fictional Framing",
        description="Wraps disallowed content in a story, thought experiment, or hypothetical.",
        keywords=[r"hypothetically", r"in a fictional", r"imagine a world", r"story about",
                  r"as a thought experiment", r"screenplay"],
    ),
    TaxonomyClass(
        key="payload_smuggling",
        name="Payload Smuggling",
        description="Splits or hides malicious content across turns, attachments, or delimiters.",
        keywords=[r"split into parts", r"continue from", r"first half", r"second half",
                  r"decode and execute", r"payload"],
    ),
    TaxonomyClass(
        key="authority_appeal",
        name="Authority / Compliance Appeal",
        description="Claims researcher, admin, safety-team, or legal authority to unlock content.",
        keywords=[r"as a researcher", r"i am an admin", r"for academic", r"safety team",
                  r"authorized user", r"my professor"],
    ),
    TaxonomyClass(
        key="chain_of_thought",
        name="Reasoning / CoT Exploit",
        description="Uses step-by-step reasoning traps or self-reflection to elicit disallowed output.",
        keywords=[r"step by step", r"let's think", r"reason through", r"chain of thought",
                  r"walk me through"],
    ),
    # 9th emerging class — multimodal / hybrid attacks not fitting cleanly above.
    TaxonomyClass(
        key="multimodal_hybrid",
        name="Multimodal / Hybrid (Emerging)",
        description="Cross-modal, tool-use, or agent-loop attacks that combine several strategies.",
        keywords=[r"image contains", r"in this screenshot", r"use the tool",
                  r"agent loop", r"function call", r"browse and"],
    ),
]

CLASS_KEYS = [c.key for c in TAXONOMY]
CLASS_NAMES = {c.key: c.name for c in TAXONOMY}
