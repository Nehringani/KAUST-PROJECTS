"""Layer 1 — RSS preprocessing and heuristic screening."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup

# --- Regex heuristics ------------------------------------------------------
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_BASE64_RE = re.compile(r"(?:[A-Za-z0-9+/]{40,}={0,2})")
_ZW_CHARS_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2066-\u2069]")
_INSTRUCTION_PATTERNS = [
    r"ignore (all|the) (previous|prior) (instructions|prompt)",
    r"disregard.*instructions?",
    r"you are now\b",
    r"system\s*:",
    r"assistant\s*:",
    r"</?system>",
    r"</?assistant>",
    r"new instructions",
    r"act as (dan|jailbroken)",
    r"reveal.*(system|hidden) (prompt|instructions?)",
]
_INSTRUCTION_RE = re.compile("|".join(_INSTRUCTION_PATTERNS), re.IGNORECASE)


@dataclass
class PreprocessResult:
    """Structured output of Layer 1."""
    cleaned_text: str
    score: int  # 0 clean, 1 suspicious, 2 likely-injected
    flags: List[str]


def _strip_html(text: str) -> str:
    """Remove tags but preserve visible text."""
    if not text:
        return ""
    return BeautifulSoup(text, "lxml").get_text(" ")


def preprocess(text: str) -> PreprocessResult:
    """Normalize a feed item and score it with lightweight heuristics."""
    flags: List[str] = []

    # 1) Detect suspicious markers BEFORE stripping — comments hide payloads.
    if _HTML_COMMENT_RE.search(text or ""):
        flags.append("html_comment")
    if _ZW_CHARS_RE.search(text or ""):
        flags.append("zero_width_or_bidi")

    # 2) Strip HTML and normalize Unicode (NFKC folds compatibility chars).
    stripped = _strip_html(text or "")
    normalized = unicodedata.normalize("NFKC", stripped)
    # Remove zero-width / bidi controls entirely after flagging.
    normalized = _ZW_CHARS_RE.sub("", normalized)

    # 3) Heuristics on the visible text.
    if _INSTRUCTION_RE.search(normalized):
        flags.append("instruction_phrase")
    if _BASE64_RE.search(normalized):
        flags.append("base64_blob")

    # 4) Scoring.
    if not flags:
        score = 0
    elif len(flags) == 1 and flags[0] in {"base64_blob"}:
        score = 1
    elif "instruction_phrase" in flags or "html_comment" in flags:
        score = 2
    else:
        score = 1

    return PreprocessResult(cleaned_text=normalized.strip(), score=score, flags=flags)
