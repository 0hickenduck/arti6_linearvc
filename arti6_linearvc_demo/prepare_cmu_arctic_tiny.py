#!/usr/bin/env python3
"""Download a tiny-aligned CMU ARCTIC slice and emit a reproducible manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from torchaudio.datasets import CMUARCTIC


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a tiny same-prompt CMU ARCTIC manifest for smoke testing."
    )
    parser.add_argument("--root", type=Path, required=True, help="Dataset root directory.")
    parser.add_argument(
        "--source-speaker",
        default="bdl",
        help="CMU ARCTIC source speaker id.",
    )
    parser.add_argument(
        "--target-speaker",
        default="slt",
        help="CMU ARCTIC target speaker id.",
    )
    parser.add_argument(
        "--num-pairs",
        type=int,
        default=1,
        help="How many same-prompt pairs to place in the manifest.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Output CSV manifest path.",
    )
    return parser.parse_args()


def load_index(root: Path, speaker: str) -> dict[str, str]:
    dataset = CMUARCTIC(root=str(root), url=speaker, download=True)
    index: dict[str, str] = {}
    for _, _, _, utterance_id in dataset:
        wav_path = (
            root
            / "ARCTIC"
            / f"cmu_us_{speaker}_arctic"
            / "wav"
            / f"arctic_{utterance_id}.wav"
        )
        index[utterance_id] = str(wav_path.resolve())
    return index


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest = args.manifest.resolve()
    manifest.parent.mkdir(parents=True, exist_ok=True)

    source_index = load_index(root, args.source_speaker)
    target_index = load_index(root, args.target_speaker)
    shared_ids = sorted(set(source_index) & set(target_index))[: args.num_pairs]
    if len(shared_ids) < args.num_pairs:
        raise RuntimeError(
            f"Only found {len(shared_ids)} shared utterance ids; requested {args.num_pairs}."
        )

    with manifest.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["utterance_id", "source_speaker", "source_wav", "target_speaker", "target_wav"],
        )
        writer.writeheader()
        for utterance_id in shared_ids:
            writer.writerow(
                {
                    "utterance_id": utterance_id,
                    "source_speaker": args.source_speaker,
                    "source_wav": source_index[utterance_id],
                    "target_speaker": args.target_speaker,
                    "target_wav": target_index[utterance_id],
                }
            )

    print(f"Wrote {len(shared_ids)} aligned pair(s) to {manifest}")
    for utterance_id in shared_ids:
        print(f"- {utterance_id}")


if __name__ == "__main__":
    main()
