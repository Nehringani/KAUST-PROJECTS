"""RoBERTa-based binary classifier for prompt-injection detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassifierConfig:
    model_name: str = "roberta-base"
    num_labels: int = 2
    max_length: int = 256


def build_model_and_tokenizer(cfg: Optional[ClassifierConfig] = None):
    """Return (model, tokenizer) using HuggingFace transformers.

    Import is done lazily so that unit tests and the preprocessor can run
    without the heavy dependency being installed.
    """
    from transformers import (  # type: ignore
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )

    cfg = cfg or ClassifierConfig()
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.model_name, num_labels=cfg.num_labels
    )
    return model, tokenizer
