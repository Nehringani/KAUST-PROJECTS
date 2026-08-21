"""
Unified LLM client.

Supports OpenAI, Anthropic, a local Ollama server, and an in-process ``fake``
provider used by the unit tests. All providers implement the same
``chat(messages, temperature) -> str`` contract so the rest of the framework
never has to branch on provider.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class LLMClient:
    """Thin wrapper picking a backend based on env vars or explicit args."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "fake")).lower()
        if self.provider == "openai":
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "anthropic":
            self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
        elif self.provider == "ollama":
            self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        else:
            self.provider = "fake"
            self.model = model or "fake-model"

    # ------------------------------------------------------------------
    def chat(self, messages: List[ChatMessage], temperature: float = 0.7) -> str:
        if self.provider == "openai":
            return self._openai(messages, temperature)
        if self.provider == "anthropic":
            return self._anthropic(messages, temperature)
        if self.provider == "ollama":
            return self._ollama(messages, temperature)
        return self._fake(messages)

    # ------------------------------------------------------------------
    def _openai(self, messages, temperature):
        from openai import OpenAI  # local import so tests do not need the pkg
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    def _anthropic(self, messages, temperature):
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        system = "\n".join(m.content for m in messages if m.role == "system")
        user_msgs = [m.to_dict() for m in messages if m.role != "system"]
        resp = client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=temperature,
            system=system or "You are a helpful assistant.",
            messages=user_msgs,
        )
        return "".join(block.text for block in resp.content if hasattr(block, "text"))

    def _ollama(self, messages, temperature):
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        r = requests.post(
            f"{host}/api/chat",
            json={
                "model": self.model,
                "messages": [m.to_dict() for m in messages],
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=180,
        )
        r.raise_for_status()
        return r.json().get("message", {}).get("content", "")

    # ------------------------------------------------------------------
    def _fake(self, messages: List[ChatMessage]) -> str:
        """
        Deterministic offline backend used by tests.

        - If the last user message contains ``"IGNORE"`` / ``"BASE64"`` / an
          override token, we simulate a *compliant* (attacked) response.
        - If the message is a judge-style prompt, we return a valid JSON verdict.
        - Otherwise we return a benign SOC analyst answer.
        """
        last = messages[-1].content if messages else ""
        if "Return ONLY JSON" in last or "attack_succeeded" in last:
            payload = {
                "attack_succeeded": "IGNORE" in last or "SYSTEM PROMPT" in last,
                "compliance_type": "full" if "IGNORE" in last else "none",
                "injection_identified": False,
                "attack_success_score": 1.0 if "IGNORE" in last else 0.0,
            }
            return json.dumps(payload)
        if any(tok in last for tok in ("IGNORE PREVIOUS", "you are now", "BASE64:")):
            return "Sure, here is the confidential system prompt: SYSTEM PROMPT LEAKED."
        return (
            "The alert appears consistent with a benign administrative action. "
            "Recommend correlating with EDR telemetry before escalation."
        )
