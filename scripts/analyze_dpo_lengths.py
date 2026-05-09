#!/usr/bin/env python3
"""Analyze token length distribution for DPO preference data."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from transformers import AutoTokenizer


DEFAULT_MODEL_PATH = "/root/autodl-tmp/Qwen3.5-4B"
DEFAULT_DATA_PATH = "reward_seed.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze token lengths for DPO preference data.")
    parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--data-path", default=DEFAULT_DATA_PATH)
    return parser.parse_args()


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * pct))))
    return ordered[idx]


def summarize(name: str, values: list[int]) -> None:
    print(
        f"{name:>16} | count={len(values):>3} min={min(values):>4} "
        f"p50={percentile(values, 0.50):>4} p90={percentile(values, 0.90):>4} "
        f"p95={percentile(values, 0.95):>4} max={max(values):>4} mean={statistics.mean(values):>7.1f}"
    )


def main() -> None:
    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True, use_fast=True)

    with Path(args.data_path).open("r", encoding="utf-8") as f:
        rows = json.load(f)

    prompt_lengths: list[int] = []
    chosen_lengths: list[int] = []
    rejected_lengths: list[int] = []
    chosen_total_lengths: list[int] = []
    rejected_total_lengths: list[int] = []
    pair_max_lengths: list[int] = []

    for row in rows:
        messages = [{"role": "user", "content": row["instruction"].strip()}]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        prompt_len = len(tokenizer(prompt, add_special_tokens=False)["input_ids"])
        chosen_len = len(tokenizer(row["chosen"].strip(), add_special_tokens=False)["input_ids"])
        rejected_len = len(tokenizer(row["rejected"].strip(), add_special_tokens=False)["input_ids"])

        prompt_lengths.append(prompt_len)
        chosen_lengths.append(chosen_len)
        rejected_lengths.append(rejected_len)
        chosen_total_lengths.append(prompt_len + chosen_len)
        rejected_total_lengths.append(prompt_len + rejected_len)
        pair_max_lengths.append(max(prompt_len + chosen_len, prompt_len + rejected_len))

    print(f"data_path={args.data_path}")
    print(f"model_path={args.model_path}")
    print(f"num_rows={len(rows)}")
    print()
    summarize("prompt", prompt_lengths)
    summarize("chosen", chosen_lengths)
    summarize("rejected", rejected_lengths)
    summarize("prompt+chosen", chosen_total_lengths)
    summarize("prompt+rejected", rejected_total_lengths)
    summarize("pair_max_total", pair_max_lengths)


if __name__ == "__main__":
    main()
