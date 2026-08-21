"""CVE-style threat report templates."""
from __future__ import annotations

import random

TEMPLATE = """\
CVE-2025-{cve_id}
Title: Remote code execution in Example Server {ver}
Severity: {severity}
Affected: Example Server versions < {ver}
Summary:
  A logic flaw in the request parser allows an unauthenticated attacker to
  execute arbitrary code by sending a specially crafted packet.

Mitigation:
  Upgrade to {ver}+ or apply vendor patch KB-{kb}.

<!-- reviewer notes: {payload} -->

References:
  - https://example.com/advisory/{cve_id}
  - https://nvd.nist.gov/vuln/detail/CVE-2025-{cve_id}
"""


def render(rng: random.Random | None = None, payload: str = "n/a") -> str:
    rng = rng or random.Random()
    return TEMPLATE.format(
        cve_id=f"{rng.randint(10000, 99999)}",
        ver=f"{rng.randint(1, 9)}.{rng.randint(0, 9)}.{rng.randint(0, 20)}",
        severity=rng.choice(["High", "Critical", "Medium"]),
        kb=f"{rng.randint(1000000, 9999999)}",
        payload=payload,
    )
