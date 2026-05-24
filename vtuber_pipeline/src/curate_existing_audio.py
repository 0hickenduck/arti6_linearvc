#!/usr/bin/env python3
import argparse
import json
import logging
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import soundfile as sf


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceItem:
    channel_id: str
    domain: str
    video_id: str
    raw_path: Path
    processing_path: Path
    processing_kind: str
    raw_duration_sec: float
    processing_duration_sec: float


def audio_info(path: Path) -> Tuple[int, int, int, float]:
    with sf.SoundFile(path) as handle:
        sample_rate = handle.samplerate
        frames = len(handle)
        channels = handle.channels
    return sample_rate, frames, channels, frames / float(sample_rate)


def find_vocal_stem(video_id: str, vocal_dirs: Sequence[Path]) -> Optional[Path]:
    for vocal_dir in vocal_dirs:
        candidate = vocal_dir / f"{video_id}_vocals.wav"
        if candidate.exists():
            return candidate
        # Fallback to wildcard search for channel_id_video_id_vocals.wav pattern
        matches = list(vocal_dir.glob(f"*_{video_id}_vocals.wav"))
        if matches:
            return matches[0]
    return None


def is_singing_domain(domain: str) -> bool:
    return "sing" in domain.lower()


def is_speech_domain(domain: str) -> bool:
    lowered = domain.lower()
    return "talk" in lowered or "speech" in lowered or "zatsudan" in lowered


def discover_sources(
    input_dir: Path,
    vocal_dirs: Sequence[Path],
    domain_contains: Sequence[str],
    channel_filter: Sequence[str],
) -> List[SourceItem]:
    sources: List[SourceItem] = []
    domain_needles = [needle.lower() for needle in domain_contains]
    channel_needles = [needle.lower() for needle in channel_filter]

    for raw_path in sorted(input_dir.rglob("*.wav")):
        rel_parts = raw_path.relative_to(input_dir).parts
        if len(rel_parts) < 3:
            logger.warning("Skipping WAV outside expected channel/domain layout: %s", raw_path)
            continue

        channel_id = rel_parts[0]
        domain = rel_parts[1]
        video_id = raw_path.stem

        if domain_needles and not any(needle in domain.lower() for needle in domain_needles):
            continue
        if channel_needles and not any(needle in channel_id.lower() for needle in channel_needles):
            continue

        vocal_stem = find_vocal_stem(video_id, vocal_dirs)
        processing_path = vocal_stem if vocal_stem is not None else raw_path
        processing_kind = "vocal_stem" if vocal_stem is not None else "raw_audio"

        _, _, _, raw_duration_sec = audio_info(raw_path)
        _, _, _, processing_duration_sec = audio_info(processing_path)

        sources.append(
            SourceItem(
                channel_id=channel_id,
                domain=domain,
                video_id=video_id,
                raw_path=raw_path,
                processing_path=processing_path,
                processing_kind=processing_kind,
                raw_duration_sec=raw_duration_sec,
                processing_duration_sec=processing_duration_sec,
            )
        )

    return sources


def frame_dbfs(path: Path, frame_ms: float) -> Tuple[np.ndarray, float]:
    with sf.SoundFile(path) as handle:
        sample_rate = handle.samplerate
        frame_size = max(1, int(round(sample_rate * frame_ms / 1000.0)))
        values: List[float] = []

        while True:
            data = handle.read(frame_size, dtype="float32", always_2d=True)
            if data.size == 0:
                break
            mono = np.mean(data, axis=1)
            rms = float(np.sqrt(np.mean(np.square(mono), dtype=np.float64)))
            values.append(20.0 * math.log10(max(rms, 1.0e-9)))

    return np.asarray(values, dtype=np.float32), frame_ms / 1000.0


def choose_threshold(db_values: np.ndarray, singing: bool) -> float:
    finite = db_values[np.isfinite(db_values)]
    if finite.size == 0:
        return -45.0

    noise_floor = float(np.percentile(finite, 20))
    offset = 8.0 if singing else 10.0
    hard_floor = -52.0 if singing else -48.0
    hard_ceiling = -25.0
    return min(max(noise_floor + offset, hard_floor), hard_ceiling)


def active_intervals(mask: np.ndarray) -> List[Tuple[int, int]]:
    intervals: List[Tuple[int, int]] = []
    start: Optional[int] = None
    for idx, value in enumerate(mask):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            intervals.append((start, idx))
            start = None
    if start is not None:
        intervals.append((start, len(mask)))
    return intervals


def fill_short_gaps(mask: np.ndarray, max_gap_frames: int) -> np.ndarray:
    if max_gap_frames <= 0:
        return mask
    filled = mask.copy()
    intervals = active_intervals(mask)
    for (_, prev_end), (next_start, _) in zip(intervals, intervals[1:]):
        if next_start - prev_end <= max_gap_frames:
            filled[prev_end:next_start] = True
    return filled


def remove_short_runs(mask: np.ndarray, min_run_frames: int) -> np.ndarray:
    if min_run_frames <= 1:
        return mask
    cleaned = mask.copy()
    for start, end in active_intervals(mask):
        if end - start < min_run_frames:
            cleaned[start:end] = False
    return cleaned


def split_interval(start_sec: float, end_sec: float, max_segment_sec: float) -> Iterable[Tuple[float, float]]:
    cursor = start_sec
    while end_sec - cursor > max_segment_sec:
        next_end = cursor + max_segment_sec
        yield cursor, next_end
        cursor = next_end
    yield cursor, end_sec


def build_segments(
    db_values: np.ndarray,
    frame_sec: float,
    duration_sec: float,
    threshold_db: float,
    singing: bool,
    args: argparse.Namespace,
) -> List[Tuple[float, float, float, float]]:
    active = db_values >= threshold_db

    gap_ms = args.singing_gap_ms if singing else args.speech_gap_ms
    pad_ms = args.singing_pad_ms if singing else args.speech_pad_ms
    min_event_ms = args.singing_min_event_ms if singing else args.speech_min_event_ms

    active = remove_short_runs(active, max(1, int(round(min_event_ms / (frame_sec * 1000.0)))))
    active = fill_short_gaps(active, max(1, int(round(gap_ms / (frame_sec * 1000.0)))))
    active = remove_short_runs(active, max(1, int(round(args.min_segment_sec / frame_sec))))

    pad_sec = pad_ms / 1000.0
    segments: List[Tuple[float, float, float, float]] = []
    for start_frame, end_frame in active_intervals(active):
        interval_start = max(0.0, start_frame * frame_sec - pad_sec)
        interval_end = min(duration_sec, end_frame * frame_sec + pad_sec)
        if interval_end - interval_start < args.min_segment_sec:
            continue

        for seg_start, seg_end in split_interval(interval_start, interval_end, args.max_segment_sec):
            if seg_end - seg_start < args.min_segment_sec:
                continue
            lo = max(0, int(seg_start / frame_sec))
            hi = min(len(db_values), max(lo + 1, int(math.ceil(seg_end / frame_sec))))
            seg_active_ratio = float(np.mean(db_values[lo:hi] >= threshold_db))
            peak_db = float(np.max(db_values[lo:hi])) if hi > lo else float("-inf")
            segments.append((seg_start, seg_end, seg_active_ratio, peak_db))

    return segments


def base_status(item: SourceItem, args: argparse.Namespace) -> Tuple[str, str]:
    channel = item.channel_id.lower()
    domain = item.domain.lower()

    if "fuwamoco" in channel:
        return "quarantine", "known_multi_speaker_or_twin_identity"

    bypass = False
    if hasattr(args, 'bypass_multi_speaker') and args.bypass_multi_speaker:
        bypass_list = [x.lower() for x in args.bypass_multi_speaker]
        if channel in bypass_list or item.video_id.lower() in bypass_list:
            bypass = True

    if not bypass and "mori" in channel and is_speech_domain(domain):
        return "review", "mori_talking_may_include_multiple_speakers"

    if is_speech_domain(domain):
        if hasattr(args, 'clean_speech_min_source_sec') and item.raw_duration_sec < args.clean_speech_min_source_sec:
            return "review", "speech_source_too_short_likely_short_or_clip"
        if item.raw_duration_sec > args.clean_speech_max_source_sec:
            return "review", "long_speech_needs_diarization"
        return "clean_candidate", "short_speech_candidate"
    if is_singing_domain(domain):
        return "clean_candidate", "singing_vocal_activity_no_asr_gate"
    return "review", "unknown_domain"


def segment_status(
    item: SourceItem,
    active_ratio: float,
    args: argparse.Namespace,
) -> Tuple[str, str]:
    status, reason = base_status(item, args)
    min_ratio = args.singing_min_active_ratio if is_singing_domain(item.domain) else args.speech_min_active_ratio
    if active_ratio < min_ratio and status == "clean_candidate":
        return "review", f"low_active_ratio:{reason}"
    return status, reason


def export_segment(source_path: Path, output_path: Path, start_sec: float, end_sec: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sf.SoundFile(source_path) as handle:
        sample_rate = handle.samplerate
        start_frame = max(0, int(round(start_sec * sample_rate)))
        frame_count = max(1, int(round((end_sec - start_sec) * sample_rate)))
        handle.seek(start_frame)
        data = handle.read(frame_count, dtype="float32", always_2d=True)
    sf.write(output_path, data, sample_rate)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Conservatively segment existing VTuber WAVs without re-downloading sources."
    )
    parser.add_argument("--input-dir", default="data/raw_audio", help="Existing raw WAV root.")
    parser.add_argument(
        "--vocal-dir",
        action="append",
        default=[],
        help="Directory containing existing <video_id>_vocals.wav stems. Can be repeated.",
    )
    parser.add_argument("--output-dir", default="data/vtuber_curated_conservative")
    parser.add_argument("--manifest", default=None, help="JSONL manifest path. Defaults under output-dir.")
    parser.add_argument(
        "--domain-contains",
        action="append",
        default=[],
        help="Only process domains containing this substring. Can be repeated.",
    )
    parser.add_argument(
        "--channel",
        action="append",
        default=[],
        help="Only process channels containing this substring. Can be repeated.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Maximum source files to process.")
    parser.add_argument("--max-source-sec", type=float, default=0.0, help="Skip source files longer than this.")
    parser.add_argument("--clean-speech-max-source-sec", type=float, default=180.0)
    parser.add_argument("--clean-speech-min-source-sec", type=float, default=300.0)
    parser.add_argument(
        "--bypass-multi-speaker",
        action="append",
        default=[],
        help="Channels or video IDs (case-insensitive) to bypass hardcoded multi-speaker flags. Can be repeated.",
    )
    parser.add_argument("--min-segment-sec", type=float, default=3.0)
    parser.add_argument("--max-segment-sec", type=float, default=15.0)
    parser.add_argument("--frame-ms", type=float, default=50.0)
    parser.add_argument("--singing-gap-ms", type=float, default=900.0)
    parser.add_argument("--speech-gap-ms", type=float, default=350.0)
    parser.add_argument("--singing-pad-ms", type=float, default=250.0)
    parser.add_argument("--speech-pad-ms", type=float, default=150.0)
    parser.add_argument("--singing-min-event-ms", type=float, default=500.0)
    parser.add_argument("--speech-min-event-ms", type=float, default=200.0)
    parser.add_argument("--singing-min-active-ratio", type=float, default=0.22)
    parser.add_argument("--speech-min-active-ratio", type=float, default=0.35)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest) if args.manifest else output_dir / "manifest.jsonl"
    vocal_dirs = [Path(path) for path in args.vocal_dir] or [Path("data/temp_demucs"), Path("data/demucs_tmp")]

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    sources = discover_sources(input_dir, vocal_dirs, args.domain_contains, args.channel)
    if args.max_source_sec > 0:
        skipped = [source for source in sources if source.raw_duration_sec > args.max_source_sec]
        sources = [source for source in sources if source.raw_duration_sec <= args.max_source_sec]
    else:
        skipped = []
    if args.limit > 0:
        sources = sources[: args.limit]

    logger.info("Discovered %d source WAVs to process; skipped %d by duration", len(sources), len(skipped))
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat()
    source_records = []
    status_counts = {}
    total_segments = 0

    with manifest_path.open("w", encoding="utf-8") as manifest_handle:
        for source_index, item in enumerate(sources, start=1):
            logger.info(
                "[%d/%d] Segmenting %s/%s/%s from %s",
                source_index,
                len(sources),
                item.channel_id,
                item.domain,
                item.video_id,
                item.processing_kind,
            )
            singing = is_singing_domain(item.domain)
            db_values, frame_sec = frame_dbfs(item.processing_path, args.frame_ms)
            threshold_db = choose_threshold(db_values, singing)
            segments = build_segments(
                db_values,
                frame_sec,
                item.processing_duration_sec,
                threshold_db,
                singing,
                args,
            )

            source_records.append(
                {
                    "channel_id": item.channel_id,
                    "domain": item.domain,
                    "video_id": item.video_id,
                    "raw_path": os.fspath(item.raw_path),
                    "processing_path": os.fspath(item.processing_path),
                    "processing_kind": item.processing_kind,
                    "raw_duration_sec": item.raw_duration_sec,
                    "processing_duration_sec": item.processing_duration_sec,
                    "threshold_db": threshold_db,
                    "segment_count": len(segments),
                }
            )

            for seg_index, (start_sec, end_sec, active_ratio, peak_db) in enumerate(segments):
                status, reason = segment_status(item, active_ratio, args)
                out_name = f"{item.video_id}_chunk{seg_index:04d}.wav"
                output_path = output_dir / status / item.channel_id / item.domain / out_name

                if args.skip_existing and output_path.exists():
                    pass
                elif not args.dry_run:
                    export_segment(item.processing_path, output_path, start_sec, end_sec)

                record = {
                    "segment_id": f"{item.channel_id}_{item.domain}_{item.video_id}_{seg_index:04d}",
                    "channel_id": item.channel_id,
                    "domain": item.domain,
                    "video_id": item.video_id,
                    "status": status,
                    "reason": reason,
                    "source_wav": os.fspath(item.raw_path),
                    "processing_wav": os.fspath(item.processing_path),
                    "processing_kind": item.processing_kind,
                    "output_wav": os.fspath(output_path),
                    "start_sec": round(start_sec, 3),
                    "end_sec": round(end_sec, 3),
                    "duration_sec": round(end_sec - start_sec, 3),
                    "active_ratio": round(active_ratio, 4),
                    "peak_db": round(peak_db, 2),
                    "threshold_db": round(threshold_db, 2),
                    "created_at": created_at,
                    "segmentation_strategy": "energy_vocal_activity_conservative_v1",
                }
                manifest_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                status_counts[status] = status_counts.get(status, 0) + 1
                total_segments += 1

    skipped_records = [
        {
            "channel_id": source.channel_id,
            "domain": source.domain,
            "video_id": source.video_id,
            "raw_path": os.fspath(source.raw_path),
            "raw_duration_sec": source.raw_duration_sec,
            "reason": "source_longer_than_max_source_sec",
        }
        for source in skipped
    ]
    summary = {
        "created_at": created_at,
        "input_dir": os.fspath(input_dir),
        "output_dir": os.fspath(output_dir),
        "manifest": os.fspath(manifest_path),
        "source_count": len(sources),
        "skipped_source_count": len(skipped_records),
        "segment_count": total_segments,
        "status_counts": status_counts,
        "domain_filters": args.domain_contains,
        "channel_filters": args.channel,
        "dry_run": args.dry_run,
        "strategy": {
            "name": "energy_vocal_activity_conservative_v1",
            "note": "Uses existing vocal stems when available; singing is not gated by ASR text.",
            "min_segment_sec": args.min_segment_sec,
            "max_segment_sec": args.max_segment_sec,
            "singing_gap_ms": args.singing_gap_ms,
            "speech_gap_ms": args.speech_gap_ms,
            "singing_pad_ms": args.singing_pad_ms,
            "speech_pad_ms": args.speech_pad_ms,
        },
    }
    write_json(output_dir / "sources.json", source_records)
    write_json(output_dir / "skipped_sources.json", skipped_records)
    write_json(output_dir / "summary.json", summary)

    logger.info("Wrote %d segments to %s", total_segments, output_dir)
    logger.info("Manifest: %s", manifest_path)


if __name__ == "__main__":
    main()
