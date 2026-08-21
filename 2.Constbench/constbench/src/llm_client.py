"""
LLM client wrapper.

Provides a single ``chat(system, user)`` entrypoint that dispatches to either
the Anthropic or OpenAI SDK depending on the ``LLM_PROVIDER`` environment
variable. Keeps the rest of the codebase provider-agnostic.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

Provider = Literal["anthropic", "openai"]


@dataclass
class LLMConfig:
    """Runtime configuration resolved from environment variables."""

    provider: Provider
    actor_model: str
    judge_model: str
    max_tokens: int
    temperature: float

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        if provider not in ("anthropic", "openai"):
            raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
        if provider == "anthropic":
            actor = os.getenv("ANTHROPIC_ACTOR_MODEL", "claude-3-5-sonnet-latest")
            judge = os.getenv("ANTHROPIC_JUDGE_MODEL", "claude-3-5-haiku-latest")
        else:
            actor = os.getenv("OPENAI_ACTOR_MODEL", "gpt-4o")
            judge = os.getenv("OPENAI_JUDGE_MODEL", "gpt-4o-mini")
        return cls(
            provider=provider,  # type: ignore[arg-type]
            actor_model=actor,
            judge_model=judge,
            max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
            temperature=float(os.getenv("TEMPERATURE", "0.2")),
        )


class LLMClient:
    """Provider-agnostic chat client."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig.from_env()
        if self.config.provider == "anthropic":
            from anthropic import Anthropic

            self._anthropic = Anthropic()
        else:
            from openai import OpenAI

            self._openai = OpenAI()

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        reraise=True,
    )
    def chat(self, system: str, user: str, *, model: str | None = None) -> str:
        """Send a single-turn chat request and return the assistant text."""
        model = model or self.config.actor_model
        if self.config.provider == "anthropic":
            resp = self._anthropic.messages.create(
                model=model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            # Concatenate all text blocks in the response.
            return "".join(
                block.text for block in resp.content if getattr(block, "type", "") == "text"
            ).strip()

        # OpenAI branch
        resp = self._openai.chat.completions.create(
            model=model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (resp.choices[0].message.content or "").strip()
