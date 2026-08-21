"""Base class shared by all attack modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Attack:
    """A single generated attack instance."""
    module: str            # "direct" | "indirect" | "multiturn" | "encoding"
    attack_class: int      # 1..8 in the SOC-RedTeam taxonomy
    injected_instruction: str
    prompt: str            # single-turn attacker prompt (context+payload merged)
    turns: List[str] = field(default_factory=list)  # only used by multi-turn
    metadata: dict = field(default_factory=dict)


class AttackModule:
    """Abstract base class for attack modules."""
    name: str = "base"
    attack_class: int = 0

    def generate(self, context_name: str, context_text: str, n: int) -> List[Attack]:
        raise NotImplementedError
