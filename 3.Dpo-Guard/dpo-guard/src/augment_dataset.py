"""
Augment a small seed set of preference pairs by paraphrasing prompts with GPT-3.5.

Each seed pair is expanded into N variants that keep the same (chosen, rejected)
semantics but vary the surface form of the prompt. This lets you grow from
~100 manual pairs to 500+ without diluting label quality.

    python src/augment_dataset.py \\
        --input data/construction/preference_pairs_v1.jsonl \\
        --output data/construction/preference_pairs_augmented.jsonl \\
        --variants 4
"""
from __future__ import annotations

import argparse
import os
import time
from typing import List

from dotenv import load_dotenv
from tqdm import tqdm

from utils import read_jsonl, write_jsonl

SYSTEM = (
    "You paraphrase cybersecurity prompts for a preference-learning dataset. "
    "Rewrite the user prompt below, preserving ALL of its content (including any "
    "malicious injection payload verbatim) but varying tone, phrasing, and framing. "
    "Return only the rewritten prompt, no commentary."
)


def paraphrase(client, prompt: str, n: int) -> List[str]:
    """Return n paraphrases of the same prompt via GPT-3.5."""
    variants: List[str] = []
    for _ in range(n):
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=400,
        )
        variants.append(resp.choices[0].message.content.strip())
    return variants


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--variants", type=int, default=4)
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set. See .env.example.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    seeds = list(read_jsonl(args.input))
    augmented: list[dict] = list(seeds)  # keep originals

    for seed in tqdm(seeds, desc="Augmenting"):
        try:
            for variant in paraphrase(client, seed["prompt"], args.variants):
                augmented.append({
                    "prompt": variant,
                    "chosen": seed["chosen"],
                    "rejected": seed["rejected"],
                    "class": seed.get("class"),
                    "source": "gpt-3.5-paraphrase",
                })
        except Exception as e:  # noqa: BLE001
            print(f"Skip one seed due to API error: {e}")
            time.sleep(2)

    write_jsonl(augmented, args.output)
    print(f"Wrote {len(augmented)} pairs to {args.output}")


if __name__ == "__main__":
    main()
