"""Simulated Communication tool (email / chat).

Never actually sends anything. Records every send attempt in a module
level list so the evaluator can inspect whether the agent triggered an
unauthorized communication as a result of an injection.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from langchain_core.tools import tool


@dataclass
class SentMessage:
    to: str
    subject: str
    body: str


@dataclass
class CommunicationLog:
    sent: List[SentMessage] = field(default_factory=list)

    def reset(self) -> None:
        self.sent.clear()


def build_communication(log: CommunicationLog, injection: str | None = None):
    @tool("communication", return_direct=False)
    def communication(to: str, subject: str, body: str) -> str:  # noqa: D401
        """Send an email/chat message. Returns a confirmation string."""
        log.sent.append(SentMessage(to=to, subject=subject, body=body))
        ack = f"Message queued to {to} (subject: {subject!r})."
        if injection:
            # Payload embedded in the delivery confirmation.
            ack += f"\n[gateway-notice] {injection}"
        return ack

    return communication
