#!/usr/bin/env python3
"""Evaluate speaker-recognition robustness across speech and singing domains."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from time import perf_counter
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

import librosa
import matplotlib
import numpy as np
import torch
import torch.nn.functional as F
from huggingface_hub import hf_hub_download
from speechbrain.inference.speaker import EncoderClassifier

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


REPO_ID = "AaronZ345/GTSinger"
DEFAULT_LANGUAGES = [
    "Chinese",
    "English",
    "French",
    "German",
    "Italian",
    "Japanese",
    "Korean",
    "Russian",
    "Spanish",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run closed-set speaker identification and verification under "
            "speech/singing domain mismatch."
        )
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-id", default=REPO_ID)
    parser.add_argument(
        "--language",
        dest="languages",
        action="append",
        default=[],
        help="Language subset to include. May be repeated. Defaults to all known GTSinger languages.",
    )
    parser.add_argument("--num-speakers", type=int, default=10)
    parser.add_argument("--enroll-per-domain", type=int, default=2)
    parser.add_argument("--query-per-domain", type=int, default=2)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--selection-strategy",
        choices=["metadata-order", "seeded-random"],
        default="metadata-order",
        help="Choose eligible speakers and rows by metadata order or seeded random sampling.",
    )
    parser.add_argument(
        "--bundle-zip",
        type=Path,
        nargs="?",
        const=Path("__default__"),
        default=None,
        help="Also write a portable zip bundle containing reports and metrics.",
    )
    return parser.parse_args()


def download_file(repo_id: str, filename: str, root: Path) -> Path:
    return Path(
        hf_hub_download(
            repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=root,
        )
    ).resolve()


def parse_item_name(item_name: str) -> dict[str, str]:
    parts = item_name.split("#")
    if len(parts) < 6:
        return {"language": "", "singer": "", "style": "", "song": "", "group": "", "take": ""}
    return {
        "language": parts[0],
        "singer": parts[1],
        "style": parts[2],
        "song": parts[3],
        "group": parts[4],
        "take": parts[5],
    }


def valid_pair(row: dict[str, Any]) -> bool:
    return bool(row.get("singer")) and bool(row.get("speech_fn")) and bool(row.get("wav_fn"))


def select_round_robin_by_song(
    rows: list[dict[str, Any]],
    count: int,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
    by_song: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_song[parse_item_name(str(row["item_name"]))["song"]].append(row)
    if rng is not None:
        for song_rows in by_song.values():
            rng.shuffle(song_rows)
    selected: list[dict[str, Any]] = []
    song_names = sorted(by_song)
    if rng is not None:
        rng.shuffle(song_names)
    while len(selected) < count:
        added = False
        for song_name in song_names:
            if not by_song[song_name]:
                continue
            selected.append(by_song[song_name].pop(0))
            added = True
            if len(selected) == count:
                break
        if not added:
            break
    if len(selected) < count:
        raise RuntimeError(f"Only selected {len(selected)} rows; requested {count}.")
    return selected


def collect_speaker_rows(
    root: Path,
    repo_id: str,
    languages: list[str],
    num_speakers: int,
    rows_per_speaker: int,
    enroll_per_speaker: int,
    selection_strategy: str,
    seed: int,
) -> list[dict[str, Any]]:
    if num_speakers < 2:
        raise ValueError("num-speakers must be >= 2")
    rng = random.Random(seed) if selection_strategy == "seeded-random" else None
    speaker_rows: list[tuple[str, str, list[dict[str, Any]]]] = []
    for language in languages:
        metadata_path = download_file(repo_id, f"processed/{language}/metadata.json", root)
        metadata = json.loads(metadata_path.read_text())
        if not isinstance(metadata, list):
            raise ValueError(f"{metadata_path} must contain a JSON list")
        by_singer: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in metadata:
            if valid_pair(row):
                by_singer[str(row["singer"])].append(row)
        for singer, rows in sorted(by_singer.items()):
            if len(rows) >= rows_per_speaker:
                speaker_rows.append(
                    (language, singer, select_round_robin_by_song(rows, rows_per_speaker, rng))
                )
    if len(speaker_rows) < num_speakers:
        raise RuntimeError(f"Only found {len(speaker_rows)} eligible speakers; requested {num_speakers}.")
    if rng is not None:
        rng.shuffle(speaker_rows)

    selected: list[dict[str, Any]] = []
    for language, singer, rows in speaker_rows[:num_speakers]:
        for index, row in enumerate(rows):
            split = "enroll" if index < enroll_per_speaker else "query"
            selected.append(
                {
                    "language": language,
                    "speaker_id": singer,
                    "split": split,
                    "item_name": str(row["item_name"]),
                    "speech_fn": str(row["speech_fn"]),
                    "singing_fn": str(row["wav_fn"]),
                }
            )
    return selected


def write_selection_manifest(selection: list[dict[str, Any]], repo_id: str, root: Path, path: Path) -> list[dict[str, str]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for pair in selection:
        speech_wav = download_file(repo_id, pair["speech_fn"], root)
        singing_wav = download_file(repo_id, pair["singing_fn"], root)
        info = parse_item_name(pair["item_name"])
        for domain, wav_path in [("speech", speech_wav), ("singing", singing_wav)]:
            rows.append(
                {
                    "speaker_id": pair["speaker_id"],
                    "language": pair["language"],
                    "domain": domain,
                    "split": pair["split"],
                    "song": info["song"],
                    "style": info["style"],
                    "take": info["take"],
                    "item_name": pair["item_name"],
                    "wav": str(wav_path),
                }
            )
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "speaker_id",
                "language",
                "domain",
                "split",
                "song",
                "style",
                "take",
                "item_name",
                "wav",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return rows


def load_wav(path: str, device: str, sr: int = 16000) -> torch.Tensor:
    wav, _ = librosa.load(path, sr=sr)
    return torch.tensor(wav, dtype=torch.float32).unsqueeze(0).to(device)


def extract_embedding(model: EncoderClassifier, wav_path: str, device: str) -> np.ndarray:
    wav = load_wav(wav_path, device)
    with torch.no_grad():
        embedding = model.encode_batch(wav).squeeze()
        embedding = F.normalize(embedding, p=2, dim=0)
    return embedding.detach().cpu().numpy().reshape(-1)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def normalize_np(array: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(array, axis=-1, keepdims=True)
    if np.any(norm == 0):
        raise ValueError("cannot normalize zero embedding")
    return array / norm


def centroid(vectors: list[np.ndarray]) -> np.ndarray:
    return normalize_np(np.stack(vectors, axis=0).mean(axis=0))


def closed_set_identification(records: list[dict[str, Any]], enroll_domain: str, query_domain: str) -> dict[str, Any]:
    enroll_by_speaker: dict[str, list[np.ndarray]] = defaultdict(list)
    for record in records:
        if record["split"] == "enroll" and record["domain"] == enroll_domain:
            enroll_by_speaker[record["speaker_id"]].append(record["embedding"])
    centroids = {speaker: centroid(vectors) for speaker, vectors in enroll_by_speaker.items()}
    if len(centroids) < 2:
        raise ValueError("need at least two enrolled speakers")

    details = []
    correct = 0
    for record in records:
        if record["split"] != "query" or record["domain"] != query_domain:
            continue
        scores = {speaker: cosine(record["embedding"], value) for speaker, value in centroids.items()}
        prediction = max(scores, key=scores.get)
        target_score = scores[record["speaker_id"]]
        impostor_scores = [score for speaker, score in scores.items() if speaker != record["speaker_id"]]
        margin = target_score - max(impostor_scores)
        is_correct = prediction == record["speaker_id"]
        correct += int(is_correct)
        details.append(
            {
                "speaker_id": record["speaker_id"],
                "language": record["language"],
                "query_domain": query_domain,
                "enroll_domain": enroll_domain,
                "prediction": prediction,
                "correct": is_correct,
                "target_score": target_score,
                "best_impostor_score": max(impostor_scores),
                "margin": margin,
                "item_name": record["item_name"],
            }
        )
    return {
        "enroll_domain": enroll_domain,
        "query_domain": query_domain,
        "num_queries": len(details),
        "accuracy": correct / len(details) if details else 0.0,
        "mean_target_score": float(np.mean([row["target_score"] for row in details])) if details else 0.0,
        "mean_margin": float(np.mean([row["margin"] for row in details])) if details else 0.0,
        "details": details,
    }


def verification_scores(records: list[dict[str, Any]], enroll_domain: str, query_domain: str) -> tuple[list[float], list[int]]:
    enroll_by_speaker: dict[str, list[np.ndarray]] = defaultdict(list)
    for record in records:
        if record["split"] == "enroll" and record["domain"] == enroll_domain:
            enroll_by_speaker[record["speaker_id"]].append(record["embedding"])
    centroids = {speaker: centroid(vectors) for speaker, vectors in enroll_by_speaker.items()}

    scores: list[float] = []
    labels: list[int] = []
    for record in records:
        if record["split"] != "query" or record["domain"] != query_domain:
            continue
        for speaker, value in centroids.items():
            scores.append(cosine(record["embedding"], value))
            labels.append(1 if speaker == record["speaker_id"] else 0)
    return scores, labels


def equal_error_rate(scores: list[float], labels: list[int]) -> dict[str, float]:
    if not scores or not labels or len(scores) != len(labels):
        raise ValueError("scores and labels must be non-empty and equally sized")
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("EER requires positive and negative trials")

    unique_scores = sorted(set(scores))
    eps = 1e-6
    thresholds = [unique_scores[0] - eps, *unique_scores, unique_scores[-1] + eps]
    best = {"eer": 1.0, "threshold": thresholds[0], "far": 1.0, "frr": 1.0}
    best_gap = float("inf")
    for threshold in thresholds:
        false_accepts = sum(1 for score, label in zip(scores, labels) if label == 0 and score >= threshold)
        false_rejects = sum(1 for score, label in zip(scores, labels) if label == 1 and score < threshold)
        far = false_accepts / negatives
        frr = false_rejects / positives
        gap = abs(far - frr)
        if gap < best_gap:
            best = {"eer": (far + frr) / 2, "threshold": threshold, "far": far, "frr": frr}
            best_gap = gap
    return best


def run_protocol(records: list[dict[str, Any]], enroll_domain: str, query_domain: str) -> dict[str, Any]:
    identification = closed_set_identification(records, enroll_domain, query_domain)
    scores, labels = verification_scores(records, enroll_domain, query_domain)
    same_scores = [score for score, label in zip(scores, labels) if label == 1]
    impostor_scores = [score for score, label in zip(scores, labels) if label == 0]
    return {
        "identification": {
            key: value for key, value in identification.items() if key != "details"
        },
        "verification": {
            **equal_error_rate(scores, labels),
            "num_trials": len(scores),
            "num_same_speaker_trials": sum(labels),
            "mean_same_speaker_score": float(np.mean(same_scores)),
            "mean_impostor_score": float(np.mean(impostor_scores)),
        },
        "details": identification["details"],
    }


def plot_protocols(protocols: dict[str, Any], path: Path) -> None:
    names = list(protocols)
    accuracy = [protocols[name]["identification"]["accuracy"] for name in names]
    eer = [protocols[name]["verification"]["eer"] for name in names]
    x = np.arange(len(names))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].bar(x, accuracy, color="#1f6f78")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=30, ha="right")
    axes[0].set_ylim(0, 1)
    axes[0].set_title("Closed-set speaker ID accuracy")
    axes[1].bar(x, eer, color="#b85c38")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=30, ha="right")
    axes[1].set_ylim(0, max(0.25, max(eer) * 1.2))
    axes[1].set_title("Speaker verification EER")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_report(summary: dict[str, Any], html_path: Path) -> str:
    plot_href = Path("plots") / "speaker_domain_protocols.png"
    rows = []
    for name, protocol in summary["protocols"].items():
        ident = protocol["identification"]
        verif = protocol["verification"]
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{name}</th>"
            f"<td>{ident['accuracy']:.3f}</td>"
            f"<td>{ident['mean_margin']:.3f}</td>"
            f"<td>{verif['eer']:.3f}</td>"
            f"<td>{verif['mean_same_speaker_score']:.3f}</td>"
            f"<td>{verif['mean_impostor_score']:.3f}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Speaker Domain Evaluation</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172026; }}
    main {{ width: min(1020px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 48px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 5vw, 3rem); }}
    table {{ width: 100%; border-collapse: collapse; margin: 24px 0; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #d8dee3; text-align: left; }}
    thead th {{ background: #f7f8f8; }}
    img {{ width: 100%; max-width: 900px; border: 1px solid #d8dee3; border-radius: 8px; }}
    code {{ background: #f7f8f8; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>Speaker Domain Evaluation</h1>
  <p>Dataset: GTSinger. Speakers: {summary['num_speakers']}. Enrollment/query pairs per domain: {summary['enroll_per_domain']} / {summary['query_per_domain']}.</p>
  <table>
    <thead><tr><th>Protocol</th><th>ID accuracy</th><th>Mean margin</th><th>EER</th><th>Same score</th><th>Impostor score</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <img src="{plot_href.as_posix()}" alt="Speaker domain protocol metrics">
  <p>Machine-readable results: <code>summary.json</code>. Selection manifest: <code>selection_manifest.csv</code>.</p>
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


def main() -> None:
    args = parse_args()
    languages = args.languages or DEFAULT_LANGUAGES
    rows_per_speaker = args.enroll_per_domain + args.query_per_domain
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = output_dir / "plots"
    arrays_dir = output_dir / "arrays"
    plots_dir.mkdir(exist_ok=True)
    arrays_dir.mkdir(exist_ok=True)

    started = perf_counter()
    selection = collect_speaker_rows(
        args.root.resolve(),
        args.repo_id,
        languages,
        args.num_speakers,
        rows_per_speaker,
        args.enroll_per_domain,
        args.selection_strategy,
        args.seed,
    )
    manifest_rows = write_selection_manifest(
        selection,
        args.repo_id,
        args.root.resolve(),
        output_dir / "selection_manifest.csv",
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        run_opts={"device": device},
    )
    model.eval()

    records: list[dict[str, Any]] = []
    for row in manifest_rows:
        embedding = extract_embedding(model, row["wav"], device)
        records.append({**row, "embedding": embedding})
    np.savez(
        arrays_dir / "embeddings.npz",
        embeddings=np.stack([record["embedding"] for record in records], axis=0),
        speaker_ids=np.asarray([record["speaker_id"] for record in records]),
        domains=np.asarray([record["domain"] for record in records]),
        splits=np.asarray([record["split"] for record in records]),
    )

    protocols = {
        "speech_enroll_to_speech_query": run_protocol(records, "speech", "speech"),
        "singing_enroll_to_singing_query": run_protocol(records, "singing", "singing"),
        "speech_enroll_to_singing_query": run_protocol(records, "speech", "singing"),
        "singing_enroll_to_speech_query": run_protocol(records, "singing", "speech"),
    }
    plot_protocols(protocols, plots_dir / "speaker_domain_protocols.png")

    summary = {
        "dataset": "GTSinger",
        "repo_id": args.repo_id,
        "languages": languages,
        "num_speakers": args.num_speakers,
        "enroll_per_domain": args.enroll_per_domain,
        "query_per_domain": args.query_per_domain,
        "selection_strategy": args.selection_strategy,
        "seed": args.seed,
        "device": device,
        "torch_version": torch.__version__,
        "embedding_extractor": "speechbrain/spkrec-ecapa-voxceleb",
        "elapsed_s": round(perf_counter() - started, 4),
        "selection_manifest": str(output_dir / "selection_manifest.csv"),
        "protocols": protocols,
        "plots": {"protocol_metrics": str(plots_dir / "speaker_domain_protocols.png")},
        "arrays": {"embeddings": str(arrays_dir / "embeddings.npz")},
    }
    bundle_path = resolve_bundle_path(args.bundle_zip, output_dir)
    if bundle_path is not None:
        summary["report_zip"] = str(bundle_path)
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    html_path = output_dir / "index.html"
    html_path.write_text(render_report(summary, html_path), encoding="utf-8")
    if bundle_path is not None:
        write_bundle(output_dir, bundle_path)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
