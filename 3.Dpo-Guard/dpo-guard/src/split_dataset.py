"""
Split a preference JSONL file into train/test (80/20, seed=42 by default).

    python src/split_dataset.py --input data/construction/preference_pairs_augmented.jsonl \\
                                --train data/train.jsonl --test data/test.jsonl
"""
from __future__ import annotations

import argparse
import random

from utils import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--ratio", type=float, default=0.8, help="Train fraction (default 0.8).")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    records = list(read_jsonl(args.input))
    rng = random.Random(args.seed)
    rng.shuffle(records)

    n_train = int(len(records) * args.ratio)
    train, test = records[:n_train], records[n_train:]
    write_jsonl(train, args.train)
    write_jsonl(test, args.test)
    print(f"Wrote {len(train)} train / {len(test)} test records.")


if __name__ == "__main__":
    main()
