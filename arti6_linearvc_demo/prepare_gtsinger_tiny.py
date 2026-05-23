#!/usr/bin/env python3
"""Download a small same-singer GTSinger speech-to-singing manifest."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from huggingface_hub import hf_hub_download


REPO_ID = "AaronZ345/GTSinger"
DEFAULT_METADATA = "processed/{language}/metadata.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a tiny GTSinger paired speech-to-singing manifest."
    )
    parser.add_argument("--root", type=Path, required=True, help="Local dataset cache root.")
    parser.add_argument("--manifest", type=Path, required=True, help="Output CSV manifest path.")
    parser.add_argument("--language", default="English")
    parser.add_argument(
        "--singer",
        default=None,
        help="Singer id such as EN-Alto-1. Defaults to the first singer with enough rows.",
    )
    parser.add_argument(
        "--song",
        default=None,
        help="Optional exact song/title filter from item_name field.",
    )
    parser.add_argument("--num-pairs", type=int, default=6)
    parser.add_argument(
        "--selection-strategy",
        choices=["metadata-order", "round-robin-songs"],
        default="metadata-order",
        help=(
            "metadata-order keeps the dataset order. round-robin-songs spreads rows "
            "across songs for a less adjacent train/test split."
        ),
    )
    parser.add_argument(
        "--repo-id",
        default=REPO_ID,
        help="Hugging Face dataset repo id.",
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
        return {"song": "", "technique": "", "take": ""}
    return {"song": parts[3], "technique": parts[4], "take": parts[5]}


def valid_pair(row: dict[str, Any]) -> bool:
    return bool(row.get("speech_fn")) and bool(row.get("wav_fn")) and bool(row.get("singer"))


def choose_rows(
    metadata: list[dict[str, Any]],
    singer: str | None,
    song: str | None,
    count: int,
    selection_strategy: str,
) -> tuple[str, list[dict[str, Any]]]:
    if count < 1:
        raise ValueError("num-pairs must be >= 1")

    candidates = [row for row in metadata if valid_pair(row)]
    if song:
        candidates = [row for row in candidates if parse_item_name(str(row["item_name"]))["song"] == song]
    if singer:
        candidates = [row for row in candidates if row.get("singer") == singer]
        if len(candidates) < count:
            raise RuntimeError(f"Only found {len(candidates)} rows for singer {singer}; requested {count}.")
        return singer, select_rows(candidates, count, selection_strategy)

    by_singer: dict[str, list[dict[str, Any]]] = {}
    for row in candidates:
        by_singer.setdefault(str(row["singer"]), []).append(row)
    for speaker, rows in sorted(by_singer.items()):
        if len(rows) >= count:
            return speaker, select_rows(rows, count, selection_strategy)
    raise RuntimeError(f"No singer has at least {count} paired rows after filters.")


def select_rows(
    rows: list[dict[str, Any]],
    count: int,
    selection_strategy: str,
) -> list[dict[str, Any]]:
    if selection_strategy == "metadata-order":
        return rows[:count]
    if selection_strategy != "round-robin-songs":
        raise ValueError(f"unknown selection strategy: {selection_strategy}")

    by_song: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        song = parse_item_name(str(row["item_name"]))["song"]
        by_song[song].append(row)

    selected: list[dict[str, Any]] = []
    song_names = sorted(by_song)
    while len(selected) < count:
        added = False
        for song_name in song_names:
            song_rows = by_song[song_name]
            if not song_rows:
                continue
            selected.append(song_rows.pop(0))
            added = True
            if len(selected) == count:
                break
        if not added:
            break
    if len(selected) < count:
        raise RuntimeError(f"Only selected {len(selected)} rows; requested {count}.")
    return selected


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest = args.manifest.resolve()
    manifest.parent.mkdir(parents=True, exist_ok=True)

    metadata_file = DEFAULT_METADATA.format(language=args.language)
    metadata_path = download_file(args.repo_id, metadata_file, root)
    metadata = json.loads(metadata_path.read_text())
    if not isinstance(metadata, list):
        raise ValueError(f"{metadata_path} must contain a JSON list")

    singer, rows = choose_rows(
        metadata,
        args.singer,
        args.song,
        args.num_pairs,
        args.selection_strategy,
    )
    with manifest.open("w", newline="") as f:
        fieldnames = [
            "utterance_id",
            "speaker_id",
            "source_domain",
            "source_wav",
            "target_domain",
            "target_wav",
            "language",
            "singer",
            "song",
            "technique",
            "take",
            "text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            info = parse_item_name(str(row["item_name"]))
            source_wav = download_file(args.repo_id, str(row["speech_fn"]), root)
            target_wav = download_file(args.repo_id, str(row["wav_fn"]), root)
            writer.writerow(
                {
                    "utterance_id": str(row["item_name"]).replace("#", "__"),
                    "speaker_id": singer,
                    "source_domain": "speech",
                    "source_wav": str(source_wav),
                    "target_domain": "singing",
                    "target_wav": str(target_wav),
                    "language": str(row.get("language", args.language)),
                    "singer": singer,
                    "song": info["song"],
                    "technique": info["technique"],
                    "take": info["take"],
                    "text": " ".join(str(token) for token in row.get("txt", [])),
                }
            )

    print(f"Wrote {len(rows)} GTSinger pair(s) for {singer} to {manifest}")
    for row in rows:
        print(f"- {row['item_name']}")


if __name__ == "__main__":
    main()
