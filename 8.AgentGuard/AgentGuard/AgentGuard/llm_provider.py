"""LLM provider abstraction.

Supports two providers:

* ``fake``  - a deterministic offline LLM (``FakeListLLM``) that lets the
  whole framework run without any API key or network access. Used for
  reproducible unit tests and for users who cannot spend money.
* ``openai`` - the real GPT-3.5 (or any chat model) via ``langchain-openai``.
"""
from __future__ import annotations

import os
from typing import Iterable, List

from dotenv import load_dotenv

load_dotenv()


def get_llm(provider: str = "fake", model: str = "gpt-3.5-turbo", responses: Iterable[str] | None = None):
    """Return a LangChain-compatible chat model.

    Parameters
    ----------
    provider:
        Either ``"fake"`` or ``"openai"``.
    model:
        Model name (only used for the OpenAI provider).
    responses:
        Optional canned responses for the fake provider. When ``None`` a
        sensible default cycle is used.
    """
    provider = provider.lower()
    if provider == "openai":
        # Imported lazily so users without the package installed can still run
        # the fake provider.
        from langchain_openai import ChatOpenAI

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and "
                "add your key, or use --provider fake."
            )
        return ChatOpenAI(model=model, temperature=0)

    if provider == "fake":
        from langchain_community.llms.fake import FakeListLLM

        default: List[str] = list(responses) if responses else [
            "I will investigate this request using the available tools.",
            "Based on the tool outputs I have gathered, here is my SOC summary.",
        ]
        return FakeListLLM(responses=default)

    raise ValueError(f"Unknown provider: {provider!r}")
