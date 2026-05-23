#!/usr/bin/env python3
"""Run a Seed-VC singing-voice-conversion pivot demo on GTSinger."""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

import librosa
import numpy as np
import soundfile as sf
import torch
import torch.nn.functional as F
from huggingface_hub import hf_hub_download
from speechbrain.inference.speaker import EncoderClassifier


REPO_ROOT = Path(__file__).resolve().parents[1]
SEEDVC_ROOT = REPO_ROOT / "external" / "seed-vc"
GTSINGER_REPO_ID = "AaronZ345/GTSinger"


@dataclass(frozen=True)
class AudioItem:
    language: str
    singer: str
    item_name: str
    song: str
    style: str
    group: str
    take: str
    speech_wav: Path
    singing_wav: Path


@dataclass(frozen=True)
class ConversionSpec:
    key: str
    label: str
    source_wav: Path
    reference_wav: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a Seed-VC zero-shot singing voice conversion demo using a real "
            "singing source and GTSinger speech/singing references."
        )
    )
    parser.add_argument("--root", type=Path, required=True, help="Local GTSinger cache root.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-id", default=GTSINGER_REPO_ID)
    parser.add_argument("--source-language", default="English")
    parser.add_argument("--source-singer", default="EN-Alto-1")
    parser.add_argument("--source-song", default=None)
    parser.add_argument("--source-index", type=int, default=0)
    parser.add_argument("--target-language", default="English")
    parser.add_argument("--target-singer", default="EN-Tenor-1")
    parser.add_argument("--target-song", default=None)
    parser.add_argument("--target-index", type=int, default=0)
    parser.add_argument("--diffusion-steps", type=int, default=8)
    parser.add_argument("--inference-cfg-rate", type=float, default=0.7)
    parser.add_argument("--length-adjust", type=float, default=1.0)
    parser.add_argument("--semi-tone-shift", type=int, default=0)
    parser.add_argument("--fp16", choices=["True", "False"], default="True")
    parser.add_argument(
        "--bundle-zip",
        type=Path,
        nargs="?",
        const=Path("__default__"),
        default=None,
        help="Also write a portable zip bundle for local listening.",
    )
    return parser.parse_args()


def parse_item_name(item_name: str) -> dict[str, str]:
    parts = item_name.split("#")
    if len(parts) < 6:
        return {"song": "", "style": "", "group": "", "take": ""}
    return {"song": parts[3], "style": parts[2], "group": parts[4], "take": parts[5]}


def download_file(repo_id: str, filename: str, root: Path) -> Path:
    return Path(
        hf_hub_download(
            repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=root,
        )
    ).resolve()


def load_metadata(repo_id: str, root: Path, language: str) -> list[dict[str, Any]]:
    metadata_path = download_file(repo_id, f"processed/{language}/metadata.json", root)
    metadata = json.loads(metadata_path.read_text())
    if not isinstance(metadata, list):
        raise ValueError(f"{metadata_path} must contain a JSON list")
    return metadata


def valid_pair(row: dict[str, Any]) -> bool:
    return bool(row.get("singer")) and bool(row.get("speech_fn")) and bool(row.get("wav_fn"))


def select_item(
    metadata: list[dict[str, Any]],
    repo_id: str,
    root: Path,
    language: str,
    singer: str,
    song: str | None,
    index: int,
) -> AudioItem:
    if index < 0:
        raise ValueError("source-index and target-index must be >= 0")
    rows = [row for row in metadata if valid_pair(row) and row.get("singer") == singer]
    if song:
        rows = [row for row in rows if parse_item_name(str(row["item_name"]))["song"] == song]
    if index >= len(rows):
        raise RuntimeError(
            f"Only found {len(rows)} rows for {language}/{singer}"
            + (f" song={song!r}" if song else "")
            + f"; requested index {index}."
        )
    row = rows[index]
    info = parse_item_name(str(row["item_name"]))
    return AudioItem(
        language=language,
        singer=singer,
        item_name=str(row["item_name"]),
        song=info["song"],
        style=info["style"],
        group=info["group"],
        take=info["take"],
        speech_wav=download_file(repo_id, str(row["speech_fn"]), root),
        singing_wav=download_file(repo_id, str(row["wav_fn"]), root),
    )


def ensure_dirs(output_dir: Path) -> dict[str, Path]:
    dirs = {
        "audio": output_dir / "audio",
        "logs": output_dir / "logs",
        "seedvc_raw": output_dir / "seedvc_raw",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    for path in [dirs["audio"], dirs["logs"]]:
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
    return dirs


def copy_audio(source: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return str(dest)


def run_seedvc_conversion(
    spec: ConversionSpec,
    output_wav: Path,
    raw_dir: Path,
    log_path: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    condition_raw_dir = raw_dir / spec.key
    if condition_raw_dir.exists():
        shutil.rmtree(condition_raw_dir)
    condition_raw_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "inference.py",
        "--source",
        str(spec.source_wav),
        "--target",
        str(spec.reference_wav),
        "--output",
        str(condition_raw_dir),
        "--diffusion-steps",
        str(args.diffusion_steps),
        "--length-adjust",
        str(args.length_adjust),
        "--inference-cfg-rate",
        str(args.inference_cfg_rate),
        "--f0-condition",
        "True",
        "--auto-f0-adjust",
        "False",
        "--semi-tone-shift",
        str(args.semi_tone_shift),
        "--fp16",
        args.fp16,
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    started = perf_counter()
    completed = subprocess.run(
        command,
        cwd=SEEDVC_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = perf_counter() - started
    log_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"Seed-VC conversion failed for {spec.key}; see {log_path}")
    generated = sorted(condition_raw_dir.glob("*.wav"))
    if len(generated) != 1:
        raise RuntimeError(f"Expected one Seed-VC wav for {spec.key}, found {len(generated)} in {condition_raw_dir}")
    copy_audio(generated[0], output_wav)
    return {
        "condition": spec.key,
        "label": spec.label,
        "source_wav": str(spec.source_wav),
        "reference_wav": str(spec.reference_wav),
        "output_wav": str(output_wav),
        "raw_output_wav": str(generated[0]),
        "log": str(log_path),
        "elapsed_s": round(elapsed, 4),
        "returncode": completed.returncode,
    }


def audio_info(path: Path) -> dict[str, Any]:
    info = sf.info(path)
    return {
        "path": str(path),
        "sample_rate": info.samplerate,
        "frames": info.frames,
        "duration_s": round(info.frames / info.samplerate, 4),
        "channels": info.channels,
    }


def load_wav_16k(path: Path, device: str) -> torch.Tensor:
    wav, _ = librosa.load(path, sr=16000, mono=True)
    return torch.tensor(wav, dtype=torch.float32).unsqueeze(0).to(device)


def speaker_embedding(model: EncoderClassifier, path: Path, device: str) -> np.ndarray:
    wav = load_wav_16k(path, device)
    with torch.no_grad():
        embedding = model.encode_batch(wav).squeeze()
        embedding = F.normalize(embedding, p=2, dim=0)
    return embedding.detach().cpu().numpy().reshape(-1)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def speaker_similarity(audio_outputs: dict[str, str]) -> dict[str, dict[str, float]]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        run_opts={"device": device},
    )
    model.eval()
    embeddings = {key: speaker_embedding(model, Path(path), device) for key, path in audio_outputs.items()}
    references = [
        "01_source_singing",
        "02_target_speech_reference",
        "03_target_singing_reference",
        "04_source_speech_reference",
    ]
    results: dict[str, dict[str, float]] = {}
    for key, embedding in embeddings.items():
        if not key.startswith("converted_"):
            continue
        results[key] = {
            ref: cosine(embedding, embeddings[ref])
            for ref in references
            if ref in embeddings
        }
    return results


def write_selection_manifest(path: Path, source: AudioItem, target: AudioItem) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "role",
                "language",
                "singer",
                "song",
                "style",
                "group",
                "take",
                "item_name",
                "speech_wav",
                "singing_wav",
            ],
        )
        writer.writeheader()
        for role, item in [("source", source), ("target", target)]:
            writer.writerow(
                {
                    "role": role,
                    "language": item.language,
                    "singer": item.singer,
                    "song": item.song,
                    "style": item.style,
                    "group": item.group,
                    "take": item.take,
                    "item_name": item.item_name,
                    "speech_wav": str(item.speech_wav),
                    "singing_wav": str(item.singing_wav),
                }
            )


def relative_href(path: Path, html_dir: Path) -> str:
    return Path(os.path.relpath(path.resolve(), html_dir.resolve())).as_posix()


def render_audio_cards(audio_outputs: dict[str, str], labels: dict[str, str], html_dir: Path) -> str:
    cards = []
    for key in sorted(audio_outputs):
        path = Path(audio_outputs[key])
        cards.append(
            "<article class=\"audio-card\">"
            f"<h3>{html.escape(labels.get(key, key))}</h3>"
            f"<audio controls preload=\"metadata\" src=\"{html.escape(relative_href(path, html_dir))}\"></audio>"
            f"<p>{html.escape(path.name)}</p>"
            "</article>"
        )
    return "\n".join(cards)


def render_similarity_rows(similarity: dict[str, dict[str, float]], labels: dict[str, str]) -> str:
    rows = []
    for key, scores in similarity.items():
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{html.escape(labels.get(key, key))}</th>"
            f"<td>{scores.get('01_source_singing', 0.0):.3f}</td>"
            f"<td>{scores.get('02_target_speech_reference', 0.0):.3f}</td>"
            f"<td>{scores.get('03_target_singing_reference', 0.0):.3f}</td>"
            f"<td>{scores.get('04_source_speech_reference', 0.0):.3f}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_report(summary: dict[str, Any], html_path: Path) -> str:
    html_dir = html_path.parent.resolve()
    labels = summary["audio_labels"]
    audio_cards = render_audio_cards(summary["audio_outputs"], labels, html_dir)
    similarity_rows = render_similarity_rows(summary["speaker_similarity"], labels)
    summary_href = relative_href(Path(summary["summary_path"]), html_dir)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Seed-VC Singing Pivot Demo</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172026; }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 48px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: 0; }}
    h2 {{ margin: 30px 0 12px; font-size: 1.35rem; }}
    h3 {{ margin: 0 0 10px; font-size: 1rem; }}
    .audio-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }}
    .audio-card {{ border: 1px solid #d8dee3; border-radius: 8px; padding: 12px; background: #f7f8f8; }}
    audio {{ width: 100%; }}
    table {{ width: 100%; border-collapse: collapse; border: 1px solid #d8dee3; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #d8dee3; text-align: left; }}
    thead th {{ background: #f7f8f8; }}
    code {{ background: #f7f8f8; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>Seed-VC Singing Pivot Demo</h1>
  <p>Source singing: {html.escape(summary['source_item']['singer'])} / {html.escape(summary['source_item']['song'])}. Target timbre: {html.escape(summary['target_item']['singer'])} / {html.escape(summary['target_item']['song'])}. F0 conditioning is enabled so the output keeps singing pitch from the source.</p>
  <section>
    <h2>Audio</h2>
    <div class="audio-grid">{audio_cards}</div>
  </section>
  <section>
    <h2>Speaker Similarity Probe</h2>
    <table>
      <thead><tr><th>Converted output</th><th>Source singing</th><th>Target speech ref</th><th>Target singing ref</th><th>Source speech ref</th></tr></thead>
      <tbody>{similarity_rows}</tbody>
    </table>
  </section>
  <p>Machine-readable run metadata: <a href="{html.escape(summary_href)}"><code>summary.json</code></a></p>
</main>
</body>
</html>
"""


def default_bundle_path(output_dir: Path) -> Path:
    return output_dir / f"{output_dir.name}_report.zip"


def resolve_bundle_path(value: Path | None, output_dir: Path) -> Path | None:
    if value is None:
        return None
    if value == Path("__default__"):
        return default_bundle_path(output_dir)
    return value.resolve()


def write_bundle(output_dir: Path, bundle_path: Path) -> None:
    root = output_dir.resolve()
    bundle_path = bundle_path.resolve()
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(bundle_path, "w", compression=ZIP_DEFLATED) as bundle:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.resolve() == bundle_path:
                continue
            arcname = root.name + "/" + path.relative_to(root).as_posix()
            bundle.write(path, arcname)


def item_summary(item: AudioItem) -> dict[str, str]:
    return {
        "language": item.language,
        "singer": item.singer,
        "item_name": item.item_name,
        "song": item.song,
        "style": item.style,
        "group": item.group,
        "take": item.take,
        "speech_wav": str(item.speech_wav),
        "singing_wav": str(item.singing_wav),
    }


def main() -> None:
    args = parse_args()
    if not SEEDVC_ROOT.exists():
        raise RuntimeError(f"Seed-VC checkout not found at {SEEDVC_ROOT}")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dirs = ensure_dirs(output_dir)
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    started = perf_counter()
    source_metadata = load_metadata(args.repo_id, root, args.source_language)
    target_metadata = (
        source_metadata
        if args.target_language == args.source_language
        else load_metadata(args.repo_id, root, args.target_language)
    )
    source_item = select_item(
        source_metadata,
        args.repo_id,
        root,
        args.source_language,
        args.source_singer,
        args.source_song,
        args.source_index,
    )
    target_item = select_item(
        target_metadata,
        args.repo_id,
        root,
        args.target_language,
        args.target_singer,
        args.target_song,
        args.target_index,
    )

    selection_manifest = output_dir / "selection_manifest.csv"
    write_selection_manifest(selection_manifest, source_item, target_item)

    audio_outputs = {
        "01_source_singing": copy_audio(source_item.singing_wav, dirs["audio"] / "01_source_singing.wav"),
        "02_target_speech_reference": copy_audio(
            target_item.speech_wav,
            dirs["audio"] / "02_target_speech_reference.wav",
        ),
        "03_target_singing_reference": copy_audio(
            target_item.singing_wav,
            dirs["audio"] / "03_target_singing_reference.wav",
        ),
        "04_source_speech_reference": copy_audio(
            source_item.speech_wav,
            dirs["audio"] / "04_source_speech_reference.wav",
        ),
    }
    audio_labels = {
        "01_source_singing": "Source singing content",
        "02_target_speech_reference": "Target speech reference",
        "03_target_singing_reference": "Target singing reference",
        "04_source_speech_reference": "Source speech reference",
        "converted_target_speech_ref": "Seed-VC: source singing -> target speech reference",
        "converted_target_singing_ref": "Seed-VC: source singing -> target singing reference",
        "converted_source_speech_ref": "Seed-VC: source singing -> source speech reference",
    }
    conversions = [
        ConversionSpec(
            "converted_target_speech_ref",
            audio_labels["converted_target_speech_ref"],
            source_item.singing_wav,
            target_item.speech_wav,
        ),
        ConversionSpec(
            "converted_target_singing_ref",
            audio_labels["converted_target_singing_ref"],
            source_item.singing_wav,
            target_item.singing_wav,
        ),
        ConversionSpec(
            "converted_source_speech_ref",
            audio_labels["converted_source_speech_ref"],
            source_item.singing_wav,
            source_item.speech_wav,
        ),
    ]

    conversion_runs = []
    for spec in conversions:
        output_wav = dirs["audio"] / f"{spec.key}.wav"
        conversion_runs.append(
            run_seedvc_conversion(
                spec,
                output_wav,
                dirs["seedvc_raw"],
                dirs["logs"] / f"{spec.key}.log",
                args,
            )
        )
        audio_outputs[spec.key] = str(output_wav)

    speaker_scores = speaker_similarity(audio_outputs)
    audio_metadata = {key: audio_info(Path(path)) for key, path in audio_outputs.items()}

    summary_path = output_dir / "summary.json"
    bundle_path = resolve_bundle_path(args.bundle_zip, output_dir)
    summary: dict[str, Any] = {
        "model_family": "Seed-VC",
        "model_source": "external/seed-vc",
        "model_url": "https://github.com/Plachtaa/seed-vc",
        "dataset": "GTSinger",
        "repo_id": args.repo_id,
        "summary_path": str(summary_path),
        "selection_manifest": str(selection_manifest),
        "source_item": item_summary(source_item),
        "target_item": item_summary(target_item),
        "seedvc_args": {
            "diffusion_steps": args.diffusion_steps,
            "length_adjust": args.length_adjust,
            "inference_cfg_rate": args.inference_cfg_rate,
            "f0_condition": True,
            "auto_f0_adjust": False,
            "semi_tone_shift": args.semi_tone_shift,
            "fp16": args.fp16,
        },
        "audio_outputs": audio_outputs,
        "audio_labels": audio_labels,
        "audio_metadata": audio_metadata,
        "conversion_runs": conversion_runs,
        "speaker_similarity": speaker_scores,
        "elapsed_s": round(perf_counter() - started, 4),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }
    if bundle_path is not None:
        summary["report_zip"] = str(bundle_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    html_path = output_dir / "index.html"
    html_path.write_text(render_report(summary, html_path), encoding="utf-8")
    if bundle_path is not None:
        write_bundle(output_dir, bundle_path)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
