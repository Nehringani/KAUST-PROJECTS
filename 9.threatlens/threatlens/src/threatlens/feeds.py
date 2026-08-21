"""Fetch real public threat-intelligence feeds.

Both CISA (RSS) and abuse.ch URLhaus (CSV) are supported. Network failures
degrade gracefully: the pipeline can always fall back to the simulated
feed samples in `simulated_feeds.py`.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import List

import feedparser
import requests

from .config import CISA_ALERTS_RSS, URLHAUS_CSV
from .logging_utils import log_event


@dataclass
class FeedItem:
    """Normalized representation of a single intelligence feed entry."""
    source: str
    title: str
    summary: str
    link: str
    published: str = ""
    tags: List[str] = field(default_factory=list)

    def as_text(self) -> str:
        """Concatenated text used by the screening layers."""
        return f"{self.title}\n\n{self.summary}"


def fetch_cisa_alerts(limit: int = 10, timeout: int = 15) -> List[FeedItem]:
    """Fetch recent CISA advisories via RSS."""
    try:
        parsed = feedparser.parse(CISA_ALERTS_RSS)
    except Exception as exc:  # noqa: BLE001
        log_event("cisa_fetch_error", error=str(exc))
        return []

    items: List[FeedItem] = []
    for entry in parsed.entries[:limit]:
        items.append(
            FeedItem(
                source="CISA",
                title=getattr(entry, "title", ""),
                summary=getattr(entry, "summary", ""),
                link=getattr(entry, "link", ""),
                published=getattr(entry, "published", ""),
            )
        )
    log_event("cisa_fetch_ok", count=len(items))
    return items


def fetch_urlhaus(limit: int = 10, timeout: int = 15) -> List[FeedItem]:
    """Fetch abuse.ch URLhaus recent malicious URLs (CSV)."""
    try:
        resp = requests.get(URLHAUS_CSV, timeout=timeout)
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        log_event("urlhaus_fetch_error", error=str(exc))
        return []

    items: List[FeedItem] = []
    # URLhaus CSV starts with commented header lines beginning with '#'.
    text = "\n".join(line for line in resp.text.splitlines() if not line.startswith("#"))
    reader = csv.reader(io.StringIO(text))
    for row in reader:
        if len(row) < 7:
            continue
        _id, date_added, url, url_status, threat, tags, *_ = row
        items.append(
            FeedItem(
                source="URLhaus",
                title=f"Malicious URL: {url[:80]}",
                summary=f"Threat: {threat}. Status: {url_status}. Tags: {tags}",
                link=url,
                published=date_added,
                tags=[t for t in tags.split(",") if t],
            )
        )
        if len(items) >= limit:
            break
    log_event("urlhaus_fetch_ok", count=len(items))
    return items


def fetch_all_public_feeds(limit_per_source: int = 10) -> List[FeedItem]:
    """Convenience helper returning items from every configured feed."""
    return fetch_cisa_alerts(limit=limit_per_source) + fetch_urlhaus(limit=limit_per_source)
