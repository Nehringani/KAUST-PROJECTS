"""Defense stack composition helpers."""
from __future__ import annotations

from . import dpo_guard, prompt_shield


def compose(prompt: str, defense: str) -> tuple[str, bool]:
    """
    Apply the requested defense stack to `prompt`.

    Returns ``(new_prompt, blocked)``. If ``blocked`` is True, the runner
    should NOT call the target model — the defense refused.
    """
    if defense == "none":
        return prompt, False
    if defense == "promptshield":
        return prompt_shield.apply(prompt)
    if defense == "dpo_guard":
        return dpo_guard.apply(prompt)
    if defense == "both":
        prompt, blocked = prompt_shield.apply(prompt)
        if blocked:
            return prompt, True
        return dpo_guard.apply(prompt)
    raise ValueError(f"unknown defense: {defense}")
