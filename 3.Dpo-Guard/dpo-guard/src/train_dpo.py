"""
DPO training script for injection resistance.

Usage (locally or inside the Colab notebook):
    python src/train_dpo.py --config configs/dpo_config.yaml --beta 0.1

The script iterates a single beta value so you can sweep in a loop:
    for b in 0.1 0.3 0.5 0.7 1.0; do
        python src/train_dpo.py --config configs/dpo_config.yaml --beta $b
    done
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import torch
import yaml
from datasets import load_dataset
from dotenv import load_dotenv
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import DPOConfig, DPOTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a DPO adapter for a single beta value.")
    parser.add_argument("--config", type=str, default="configs/dpo_config.yaml")
    parser.add_argument("--beta", type=float, required=True, help="Single beta to train.")
    parser.add_argument("--output-subdir", type=str, default=None,
                        help="Override output directory suffix (defaults to beta_<value>).")
    return parser.parse_args()


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_bnb_config(cfg: dict) -> BitsAndBytesConfig:
    """Assemble the 4-bit quantization config so 7B models fit on a T4 (15GB VRAM)."""
    q = cfg["quantization"]
    dtype = getattr(torch, q["bnb_4bit_compute_dtype"])
    return BitsAndBytesConfig(
        load_in_4bit=q["load_in_4bit"],
        bnb_4bit_quant_type=q["bnb_4bit_quant_type"],
        bnb_4bit_compute_dtype=dtype,
        bnb_4bit_use_double_quant=q["bnb_4bit_use_double_quant"],
    )


def main() -> None:
    load_dotenv()
    args = parse_args()
    cfg = load_config(args.config)

    model_name = cfg["model"]["name"]
    print(f"[DPO-Guard] Loading base model: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=cfg["model"]["trust_remote_code"],
    )
    # DPOTrainer requires an explicit pad token.
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=build_bnb_config(cfg),
        device_map="auto",
        trust_remote_code=cfg["model"]["trust_remote_code"],
    )
    model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(**cfg["lora"])
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    # Load preference dataset. Each JSONL record must have keys: prompt, chosen, rejected.
    data_files = {"train": cfg["data"]["train_file"], "test": cfg["data"]["eval_file"]}
    dataset = load_dataset("json", data_files=data_files)
    for split in ("train", "test"):
        required = {"prompt", "chosen", "rejected"}
        missing = required - set(dataset[split].column_names)
        if missing:
            raise ValueError(f"Split '{split}' missing keys: {missing}")

    # Output directory encodes the beta so a sweep produces one adapter per value.
    subdir = args.output_subdir or f"beta_{args.beta}"
    output_dir = Path(cfg["output"]["adapters_dir"]) / subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    d = cfg["dpo"]
    dpo_config = DPOConfig(
        output_dir=str(output_dir),
        beta=args.beta,
        num_train_epochs=d["num_train_epochs"],
        per_device_train_batch_size=d["per_device_train_batch_size"],
        gradient_accumulation_steps=d["gradient_accumulation_steps"],
        learning_rate=d["learning_rate"],
        lr_scheduler_type=d["lr_scheduler_type"],
        warmup_ratio=d["warmup_ratio"],
        max_length=d["max_length"],
        max_prompt_length=d["max_prompt_length"],
        logging_steps=d["logging_steps"],
        save_strategy=d["save_strategy"],
        fp16=d["fp16"],
        seed=d["seed"],
        report_to="none",
        remove_unused_columns=False,
    )

    # DPOTrainer automatically creates the frozen reference-model copy internally
    # (pi_ref in the loss). No manual reference model management needed.
    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=dpo_config,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        tokenizer=tokenizer,
    )

    print(f"[DPO-Guard] Training with beta={args.beta} -> {output_dir}")
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"[DPO-Guard] Done. Adapter saved to: {output_dir}")


if __name__ == "__main__":
    main()
