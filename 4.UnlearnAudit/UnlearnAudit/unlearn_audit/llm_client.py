"""Backend-agnostic LLM client: ollama | openai | anthropic."""
from __future__ import annotations
import requests
from .config import CONFIG


class LLMClient:
    def __init__(self, backend: str | None = None):
        self.backend = (backend or CONFIG.backend).lower()

    def generate(self, prompt: str) -> str:
        if self.backend == "ollama":
            return self._ollama(prompt)
        if self.backend == "openai":
            return self._openai(prompt)
        if self.backend == "anthropic":
            return self._anthropic(prompt)
        raise ValueError(f"Unknown backend: {self.backend}")

    # ---- Ollama (local, free) ----
    def _ollama(self, prompt: str) -> str:
        url = f"{CONFIG.ollama_host}/api/generate"
        payload = {
            "model": CONFIG.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": CONFIG.temperature,
                "num_predict": CONFIG.max_tokens,
            },
        }
        r = requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "")

    # ---- OpenAI ----
    def _openai(self, prompt: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=CONFIG.openai_api_key)
        resp = client.chat.completions.create(
            model=CONFIG.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=CONFIG.temperature,
            max_tokens=CONFIG.max_tokens,
        )
        return resp.choices[0].message.content or ""

    # ---- Anthropic ----
    def _anthropic(self, prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=CONFIG.anthropic_api_key)
        resp = client.messages.create(
            model=CONFIG.anthropic_model,
            max_tokens=CONFIG.max_tokens,
            temperature=CONFIG.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [block.text for block in resp.content if getattr(block, "type", "") == "text"]
        return "\n".join(parts)
