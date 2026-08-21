"""Fine-tune RoBERTa on the PromptShield dataset.

Run:
    python -m src.models.trainer

By default reads data/processed/augmented_dataset.csv and writes checkpoints
to ./checkpoints/ and metrics to ./results/classification_report.json.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

import numpy as np

from src.data.preprocessor import normalize_text
from src.models.classifier import ClassifierConfig, build_model_and_tokenizer

RANDOM_SEED = 42
ROOT = Path(__file__).resolve().parents[2]
DATA_CSV = ROOT / "data" / "processed" / "augmented_dataset.csv"
CHECKPOINT_DIR = ROOT / "checkpoints"
RESULTS_DIR = ROOT / "results"
CHECKPOINT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def compute_metrics(eval_pred) -> Dict[str, float]:
    """F1, accuracy AND the security-critical False Negative Rate.

    FNR = missed injections / total injections.
    """
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    tp = int(np.sum((predictions == 1) & (labels == 1)))
    fp = int(np.sum((predictions == 1) & (labels == 0)))
    tn = int(np.sum((predictions == 0) & (labels == 0)))
    fn = int(np.sum((predictions == 0) & (labels == 1)))

    accuracy = (tp + tn) / max(1, tp + tn + fp + fn)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-8, precision + recall)
    fnr = fn / max(1, tp + fn)  # security-critical primary metric
    fpr = fp / max(1, fp + tn)
    return {
        "f1": f1,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "false_negative_rate": fnr,
        "false_positive_rate": fpr,
    }


def main() -> None:
    import pandas as pd
    from datasets import Dataset  # type: ignore
    from transformers import (  # type: ignore
        DataCollatorWithPadding,
        EarlyStoppingCallback,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    set_seed(RANDOM_SEED)

    df = pd.read_csv(DATA_CSV)
    df["text"] = df["text"].astype(str).map(normalize_text)

    # 70/15/15 split, stratified on binary label.
    from sklearn.model_selection import train_test_split

    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=RANDOM_SEED, stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=RANDOM_SEED, stratify=temp_df["label"]
    )
    print(f"train={len(train_df)} val={len(val_df)} test={len(test_df)}")

    cfg = ClassifierConfig()
    model, tokenizer = build_model_and_tokenizer(cfg)

    def tokenize(batch):
        return tokenizer(
            batch["text"], truncation=True, max_length=cfg.max_length
        )

    def to_ds(pdf):
        ds = Dataset.from_pandas(pdf[["text", "label"]].reset_index(drop=True))
        ds = ds.map(tokenize, batched=True)
        return ds

    train_ds, val_ds, test_ds = to_ds(train_df), to_ds(val_df), to_ds(test_df)

    args = TrainingArguments(
        output_dir=str(CHECKPOINT_DIR),
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
        warmup_steps=100,
        weight_decay=0.01,
        fp16=os.environ.get("FP16", "1") == "1",
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=25,
        report_to=[],
        seed=RANDOM_SEED,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    trainer.train()

    # Held-out test evaluation — never used for tuning.
    test_metrics = trainer.evaluate(test_ds, metric_key_prefix="test")
    print(json.dumps(test_metrics, indent=2))

    (RESULTS_DIR / "classification_report.json").write_text(
        json.dumps(test_metrics, indent=2)
    )

    # Save final artefacts.
    trainer.save_model(str(CHECKPOINT_DIR / "final"))
    tokenizer.save_pretrained(str(CHECKPOINT_DIR / "final"))
    print(f"Model saved to {CHECKPOINT_DIR / 'final'}")


if __name__ == "__main__":
    main()
