"""
Constitution loader and container.

A Constitution is a validated set of principles loaded from YAML. Each
principle has an ``id``, ``name``, ``principle`` text, ``rationale`` and
an ``applies_to`` list of SOC contexts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Principle:
    """A single constitutional principle."""

    id: str
    name: str
    principle: str
    rationale: str
    applies_to: list[str] = field(default_factory=lambda: ["all"])

    def applies_to_category(self, category: str) -> bool:
        """Return True if this principle applies to the given SOC category."""
        return "all" in self.applies_to or category in self.applies_to


@dataclass
class Constitution:
    """A validated collection of principles loaded from YAML."""

    id: str
    name: str
    version: int
    description: str
    principles: list[Principle]

    @classmethod
    def load(cls, path: str | Path) -> "Constitution":
        raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        principles = [Principle(**p) for p in raw["principles"]]
        return cls(
            id=raw["id"],
            name=raw["name"],
            version=int(raw.get("version", 1)),
            description=raw.get("description", ""),
            principles=principles,
        )

    def principle_by_id(self, pid: str) -> Principle | None:
        for p in self.principles:
            if p.id == pid:
                return p
        return None

    def as_system_prompt(self) -> str:
        """Render the full constitution as a system-prompt preamble."""
        lines = [
            f"You are a Security Operations Center (SOC) assistant governed by",
            f"the following constitution: {self.name}.",
            "",
            "You MUST follow every principle below. When a request conflicts",
            "with a principle, the principle wins.",
            "",
        ]
        for p in self.principles:
            lines.append(f"[{p.id}] {p.name}")
            lines.append(p.principle.strip())
            lines.append("")
        return "\n".join(lines)
