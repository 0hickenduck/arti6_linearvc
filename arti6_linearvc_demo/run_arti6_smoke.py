#!/usr/bin/env python3
"""Run a tiny ARTI-6 inversion+synthesis smoke test over one or more wav files."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from time import perf_counter

import soundfile as sf
import torch


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTI6_ROOT = REPO_ROOT / "external" / "arti-6"
sys.path.insert(0, str(ARTI6_ROOT / "arti6"))

from arti6 import ARTI6  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ARTI-6 on a tiny list of wav files and save reconstruction artifacts."
    )
    parser.add_argument(
        "--wav",
        action="append",
        required=True,
        help="Input wav path. Repeat --wav for multiple samples.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where reconstructions and summary.json are written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_paths = [
        (REPO_ROOT / raw_wav).resolve() if not Path(raw_wav).is_absolute() else Path(raw_wav)
        for raw_wav in args.wav
    ]
    os.chdir(ARTI6_ROOT)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    started = perf_counter()

    model = ARTI6(device=device)
    model.load_model()
    model_load_s = perf_counter() - started

    results = []
    for sample_index, wav_path in enumerate(wav_paths, start=1):
        sample_started = perf_counter()
        inverted = model.invert(wav_path=str(wav_path))
        reconstructed = model.synthesize(
            inverted["arti_feats"],
            inverted["spk_emb"],
        )

        output_wav = output_dir / f"{sample_index:02d}_{wav_path.stem}_reconstructed.wav"
        sf.write(output_wav, reconstructed, 16000)

        results.append(
            {
                "input_wav": str(wav_path),
                "output_wav": str(output_wav),
                "arti_feats_shape": list(inverted["arti_feats"].shape),
                "spk_emb_shape": list(inverted["spk_emb"].shape),
                "elapsed_s": round(perf_counter() - sample_started, 4),
            }
        )

    summary = {
        "device": device,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "model_load_s": round(model_load_s, 4),
        "samples": results,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
