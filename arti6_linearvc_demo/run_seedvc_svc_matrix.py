#!/usr/bin/env python3
"""Run a small matrix of Seed-VC singing conversion demos and aggregate results."""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_SCRIPT = REPO_ROOT / "arti6_linearvc_demo" / "run_seedvc_svc_demo.py"
SUBJECTIVE_SCRIPT = REPO_ROOT / "arti6_linearvc_demo" / "build_subjective_eval.py"


@dataclass(frozen=True)
class PairSpec:
    pair_id: str
    source_language: str
    source_singer: str
    source_song: str
    target_language: str
    target_singer: str
    target_song: str


ENGLISH_TRIANGLE = [
    PairSpec(
        "en_alto1_to_en_tenor1",
        "English",
        "EN-Alto-1",
        "yesterday once more",
        "English",
        "EN-Tenor-1",
        "Firework",
    ),
    PairSpec(
        "en_tenor1_to_en_alto2",
        "English",
        "EN-Tenor-1",
        "Firework",
        "English",
        "EN-Alto-2",
        "Call Me Maybe",
    ),
    PairSpec(
        "en_alto2_to_en_alto1",
        "English",
        "EN-Alto-2",
        "Call Me Maybe",
        "English",
        "EN-Alto-1",
        "yesterday once more",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a reproducible Seed-VC SVC matrix and aggregate speaker/timbre diagnostics."
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pairs-csv", type=Path, default=None)
    parser.add_argument(
        "--preset",
        choices=["english-triangle"],
        default="english-triangle",
        help="Built-in pair matrix used when --pairs-csv is omitted.",
    )
    parser.add_argument("--diffusion-steps", type=int, default=30)
    parser.add_argument("--inference-cfg-rate", type=float, default=0.7)
    parser.add_argument("--length-adjust", type=float, default=1.0)
    parser.add_argument("--semi-tone-shift", type=int, default=0)
    parser.add_argument("--fp16", choices=["True", "False"], default="True")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Reuse a completed pair run when its summary.json already exists.",
    )
    parser.add_argument(
        "--bundle-zip",
        type=Path,
        nargs="?",
        const=Path("__default__"),
        default=None,
        help="Write a portable zip containing the aggregate report and all pair run artifacts.",
    )
    return parser.parse_args()


def load_pairs_from_csv(path: Path) -> list[PairSpec]:
    with path.open() as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a CSV header")
        required = {
            "pair_id",
            "source_language",
            "source_singer",
            "source_song",
            "target_language",
            "target_singer",
            "target_song",
        }
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} is missing required column(s): {', '.join(sorted(missing))}")
        return [
            PairSpec(
                pair_id=row["pair_id"],
                source_language=row["source_language"],
                source_singer=row["source_singer"],
                source_song=row["source_song"],
                target_language=row["target_language"],
                target_singer=row["target_singer"],
                target_song=row["target_song"],
            )
            for row in reader
        ]


def load_pair_specs(args: argparse.Namespace) -> list[PairSpec]:
    if args.pairs_csv is not None:
        pairs = load_pairs_from_csv(args.pairs_csv)
    elif args.preset == "english-triangle":
        pairs = ENGLISH_TRIANGLE
    else:
        raise ValueError(f"unknown preset: {args.preset}")
    if not pairs:
        raise ValueError("pair matrix must contain at least one pair")
    return pairs


def run_command(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"command failed with code {completed.returncode}; see {log_path}")


def run_pair(pair: PairSpec, args: argparse.Namespace, pair_dir: Path, logs_dir: Path) -> dict[str, Any]:
    summary_path = pair_dir / "summary.json"
    if args.skip_existing and summary_path.exists():
        return json.loads(summary_path.read_text())

    command = [
        sys.executable,
        str(DEMO_SCRIPT),
        "--root",
        str(args.root.resolve()),
        "--output-dir",
        str(pair_dir),
        "--source-language",
        pair.source_language,
        "--source-singer",
        pair.source_singer,
        "--source-song",
        pair.source_song,
        "--target-language",
        pair.target_language,
        "--target-singer",
        pair.target_singer,
        "--target-song",
        pair.target_song,
        "--diffusion-steps",
        str(args.diffusion_steps),
        "--inference-cfg-rate",
        str(args.inference_cfg_rate),
        "--length-adjust",
        str(args.length_adjust),
        "--semi-tone-shift",
        str(args.semi_tone_shift),
        "--fp16",
        args.fp16,
    ]
    run_command(command, logs_dir / f"{pair.pair_id}_run.log")

    subjective_command = [
        sys.executable,
        str(SUBJECTIVE_SCRIPT),
        "--summary",
        str(summary_path),
        "--reference-condition",
        "03_target_singing_reference",
    ]
    run_command(subjective_command, logs_dir / f"{pair.pair_id}_subjective.log")
    return json.loads(summary_path.read_text())


def metric_row(pair: PairSpec, summary: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    similarity = summary["speaker_similarity"]
    speech_prompt = similarity["converted_target_speech_ref"]
    singing_prompt = similarity["converted_target_singing_ref"]
    source_prompt = similarity["converted_source_speech_ref"]
    return {
        "pair_id": pair.pair_id,
        "source_singer": pair.source_singer,
        "source_song": pair.source_song,
        "target_singer": pair.target_singer,
        "target_song": pair.target_song,
        "speech_prompt_to_target_speech": speech_prompt["02_target_speech_reference"],
        "speech_prompt_to_target_singing": speech_prompt["03_target_singing_reference"],
        "speech_prompt_to_source_singing": speech_prompt["01_source_singing"],
        "speech_prompt_to_source_speech": speech_prompt["04_source_speech_reference"],
        "singing_prompt_to_target_speech": singing_prompt["02_target_speech_reference"],
        "singing_prompt_to_target_singing": singing_prompt["03_target_singing_reference"],
        "singing_prompt_to_source_singing": singing_prompt["01_source_singing"],
        "source_prompt_to_source_singing": source_prompt["01_source_singing"],
        "source_prompt_to_source_speech": source_prompt["04_source_speech_reference"],
        "speech_prompt_target_advantage": max(
            speech_prompt["02_target_speech_reference"],
            speech_prompt["03_target_singing_reference"],
        )
        - max(
            speech_prompt["01_source_singing"],
            speech_prompt["04_source_speech_reference"],
        ),
        "singing_prompt_target_advantage": max(
            singing_prompt["02_target_speech_reference"],
            singing_prompt["03_target_singing_reference"],
        )
        - max(
            singing_prompt["01_source_singing"],
            singing_prompt["04_source_speech_reference"],
        ),
        "run_dir": str(run_dir),
        "index_html": str(run_dir / "index.html"),
        "subjective_eval_html": str(run_dir / "subjective_eval.html"),
    }


def write_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return html.escape(str(value))


def relative_href(path: Path, html_dir: Path) -> str:
    return Path(os.path.relpath(path.resolve(), html_dir.resolve())).as_posix()


def render_matrix_rows(rows: list[dict[str, Any]], html_dir: Path) -> str:
    rendered = []
    for row in rows:
        rendered.append(
            "<tr>"
            f"<th scope=\"row\">{html.escape(row['pair_id'])}</th>"
            f"<td>{html.escape(row['source_singer'])} -> {html.escape(row['target_singer'])}</td>"
            f"<td>{fmt(row['speech_prompt_to_target_speech'])}</td>"
            f"<td>{fmt(row['speech_prompt_to_target_singing'])}</td>"
            f"<td>{fmt(row['speech_prompt_target_advantage'])}</td>"
            f"<td>{fmt(row['singing_prompt_to_target_singing'])}</td>"
            f"<td>{fmt(row['singing_prompt_target_advantage'])}</td>"
            f"<td>{fmt(row['source_prompt_to_source_speech'])}</td>"
            f"<td><a href=\"{html.escape(relative_href(Path(row['index_html']), html_dir))}\">report</a></td>"
            f"<td><a href=\"{html.escape(relative_href(Path(row['subjective_eval_html']), html_dir))}\">blind eval</a></td>"
            "</tr>"
        )
    return "\n".join(rendered)


def render_report(summary: dict[str, Any], rows: list[dict[str, Any]], html_path: Path) -> str:
    html_dir = html_path.parent.resolve()
    matrix_rows = render_matrix_rows(rows, html_dir)
    metrics_href = relative_href(Path(summary["metrics_csv"]), html_dir)
    summary_href = relative_href(Path(summary["summary_path"]), html_dir)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Seed-VC SVC Matrix</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172026; }}
    main {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 48px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: 0; }}
    table {{ width: 100%; border-collapse: collapse; border: 1px solid #d8dee3; margin-top: 20px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #d8dee3; text-align: left; vertical-align: top; }}
    thead th {{ background: #f7f8f8; }}
    code {{ background: #f7f8f8; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>Seed-VC SVC Matrix</h1>
  <p>Preset: {html.escape(summary['preset'])}. Diffusion steps: {summary['diffusion_steps']}. Each pair keeps source singing content/F0 and changes the reference prompt.</p>
  <table>
    <thead>
      <tr>
        <th>Pair</th><th>Direction</th><th>Speech prompt -> target speech</th>
        <th>Speech prompt -> target singing</th><th>Speech target advantage</th>
        <th>Singing prompt -> target singing</th><th>Singing target advantage</th>
        <th>Source prompt -> source speech</th><th>Report</th><th>Blind eval</th>
      </tr>
    </thead>
    <tbody>{matrix_rows}</tbody>
  </table>
  <p><a href="{html.escape(metrics_href)}"><code>matrix_metrics.csv</code></a> | <a href="{html.escape(summary_href)}"><code>matrix_summary.json</code></a></p>
</main>
</body>
</html>
"""


def aggregate_stats(rows: list[dict[str, Any]]) -> dict[str, float]:
    numeric_keys = [
        "speech_prompt_to_target_speech",
        "speech_prompt_to_target_singing",
        "speech_prompt_target_advantage",
        "singing_prompt_to_target_singing",
        "singing_prompt_target_advantage",
        "source_prompt_to_source_speech",
    ]
    return {
        f"mean_{key}": float(sum(float(row[key]) for row in rows) / len(rows))
        for key in numeric_keys
    }


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
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    runs_dir = output_dir / "runs"
    logs_dir = output_dir / "logs"
    runs_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    started = perf_counter()
    pairs = load_pair_specs(args)
    rows: list[dict[str, Any]] = []
    run_summaries: dict[str, Any] = {}
    for pair in pairs:
        pair_dir = runs_dir / pair.pair_id
        summary = run_pair(pair, args, pair_dir, logs_dir)
        run_summaries[pair.pair_id] = {
            "summary_path": str(pair_dir / "summary.json"),
            "source_item": summary["source_item"],
            "target_item": summary["target_item"],
            "speaker_similarity": summary["speaker_similarity"],
        }
        rows.append(metric_row(pair, summary, pair_dir))

    metrics_csv = output_dir / "matrix_metrics.csv"
    write_metrics_csv(metrics_csv, rows)
    summary_path = output_dir / "matrix_summary.json"
    bundle_path = resolve_bundle_path(args.bundle_zip, output_dir)
    summary: dict[str, Any] = {
        "preset": args.preset,
        "pairs_csv": str(args.pairs_csv.resolve()) if args.pairs_csv else None,
        "num_pairs": len(pairs),
        "diffusion_steps": args.diffusion_steps,
        "inference_cfg_rate": args.inference_cfg_rate,
        "length_adjust": args.length_adjust,
        "semi_tone_shift": args.semi_tone_shift,
        "fp16": args.fp16,
        "elapsed_s": round(perf_counter() - started, 4),
        "metrics_csv": str(metrics_csv),
        "summary_path": str(summary_path),
        "aggregate_stats": aggregate_stats(rows),
        "rows": rows,
        "run_summaries": run_summaries,
    }
    if bundle_path is not None:
        summary["report_zip"] = str(bundle_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    html_path = output_dir / "index.html"
    html_path.write_text(render_report(summary, rows, html_path), encoding="utf-8")
    if bundle_path is not None:
        write_bundle(output_dir, bundle_path)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
