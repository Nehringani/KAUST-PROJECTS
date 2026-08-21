"""Layer 3 — strict Pydantic schema for synthesis output."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator


class ThreatLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ThreatIntelReport(BaseModel):
    """Canonical structured report emitted by the synthesizer.

    A schema violation (injected string where a list/int/enum is expected)
    causes the item to be flagged as invalid and returned to the analyst.
    """
    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(min_length=1, max_length=2000)
    threat_level: ThreatLevel
    ioc_count: int = Field(ge=0, le=10_000)
    threat_actors: List[str] = Field(default_factory=list, max_length=25)
    affected_sectors: List[str] = Field(default_factory=list, max_length=25)
    mitre_ttps: List[str] = Field(default_factory=list, max_length=50)
    injection_flagged: bool = False
    source_url: Optional[str] = None

    @field_validator("threat_actors", "affected_sectors", "mitre_ttps", mode="before")
    @classmethod
    def _reject_string_where_list_expected(cls, v):
        # Injection commonly tries to overwrite lists with a single string
        # containing hidden instructions. Reject non-list types explicitly.
        if isinstance(v, str):
            raise ValueError("Expected list, got string (possible injection).")
        return v


def validate_report(payload: dict) -> tuple[Optional[ThreatIntelReport], Optional[str]]:
    """Return (report, error). Exactly one is None."""
    try:
        return ThreatIntelReport(**payload), None
    except ValidationError as exc:
        return None, str(exc)
