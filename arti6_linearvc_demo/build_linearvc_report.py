#!/usr/bin/env python3
"""Build a static local report for a LinearVC floor experiment output."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


CONDITION_LABELS = {
    "01_source_reconstruction": "Source reconstruction",
    "02_target_reconstruction": "Target reconstruction",
    "03_embedding_only_vc": "Embedding-only VC",
    "04_oracle_target_arti_plus_source_spk": "Oracle: target articulation + source speaker",
    "05_source_arti_plus_average_spk": "Control: source articulation + average speaker",
    "06_target_arti_plus_average_spk": "Oracle: target articulation + average speaker",
    "07_pure_meanstd_transform_plus_source_spk": "Pure: mean/std transform + source speaker",
    "08_pure_diag_affine_transform_plus_source_spk": "Pure: diagonal affine + source speaker",
    "09_pure_full_affine_transform_plus_source_spk": "Pure: full affine + source speaker",
    "10_average_meanstd_transform_plus_average_spk": "Average: mean/std transform + average speaker",
    "11_average_diag_affine_transform_plus_average_spk": "Average: diagonal affine + average speaker",
    "12_average_full_affine_transform_plus_average_spk": "Average: full affine + average speaker",
    "13_hybrid_meanstd_transform_plus_target_spk": "Hybrid: mean/std transform + target speaker",
    "14_hybrid_diag_affine_transform_plus_target_spk": "Hybrid: diagonal affine + target speaker",
    "15_hybrid_full_affine_transform_plus_target_spk": "Hybrid: full affine + target speaker",
    "04_meanstd_transform_plus_target_spk": "Mean/std transform + target speaker",
    "05_diag_affine_transform_plus_target_spk": "Diagonal affine transform + target speaker",
    "06_full_affine_transform_plus_target_spk": "Full affine transform + target speaker",
}

METRIC_LABELS = {
    "source_identity": "Source identity",
    "meanstd": "Mean/std transform",
    "diag_affine": "Diagonal affine",
    "full_affine": "Full affine",
}

PLOT_LABELS = {
    "trajectories": "Aligned articulatory trajectories",
    "meanstd_comparison": "Per-dimension mean/std comparison",
    "full_affine_heatmap": "Full affine weight matrix",
}


def decode_tag_number(value: str) -> str:
    return value.replace("p", ".")


def display_label(key: str) -> str:
    if key in CONDITION_LABELS:
        return CONDITION_LABELS[key]
    if key.startswith("ridge_pure_lam_") and key.endswith("_plus_source_spk"):
        value = key.removeprefix("ridge_pure_lam_").removesuffix("_plus_source_spk")
        return f"Ridge pure: full affine lambda={decode_tag_number(value)} + source speaker"
    if key.startswith("ridge_hybrid_lam_") and key.endswith("_plus_target_spk"):
        value = key.removeprefix("ridge_hybrid_lam_").removesuffix("_plus_target_spk")
        return f"Ridge hybrid: full affine lambda={decode_tag_number(value)} + target speaker"
    if key.startswith("alpha_pure_") and key.endswith("_plus_source_spk"):
        body = key.removeprefix("alpha_pure_").removesuffix("_plus_source_spk")
        transform, alpha = body.rsplit("_a_", 1)
        if transform.startswith("ridge_full_affine_lam_"):
            value = transform.removeprefix("ridge_full_affine_lam_")
            transform_label = f"ridge full affine lambda={decode_tag_number(value)}"
        else:
            transform_label = transform.replace("_", " ")
        return f"Alpha pure: {transform_label}, alpha={decode_tag_number(alpha)} + source speaker"
    return key.replace("_", " ").title()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a static HTML report from a LinearVC floor summary.json."
    )
    parser.add_argument(
        "--summary",
        type=Path,
        required=True,
        help="Path to the experiment summary.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path for the generated HTML. Defaults to index.html beside summary.json.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Render the page even if referenced audio or plot files are missing.",
    )
    parser.add_argument(
        "--bundle-zip",
        type=Path,
        nargs="?",
        const=Path("__default__"),
        default=None,
        help=(
            "Also write a portable zip bundle containing index.html, summary.json, "
            "audio, and plots. Defaults to <output-dir>/<output-dir-name>_report.zip."
        ),
    )
    return parser.parse_args()


def load_summary(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def as_path(value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"summary field {field!r} must be a non-empty string path")
    return Path(value)


def resolve_artifact(path_value: object, summary_dir: Path, field: str) -> Path:
    path = as_path(path_value, field)
    if path.is_absolute():
        return path
    return (summary_dir / path).resolve()


def relative_href(path: Path, html_dir: Path) -> str:
    return Path(os.path.relpath(path.resolve(), html_dir.resolve())).as_posix()


def validate_artifacts(
    summary: dict[str, Any],
    summary_dir: Path,
    allow_missing: bool,
) -> tuple[dict[str, Path], dict[str, Path], list[str]]:
    missing: list[str] = []
    audio = collect_paths(summary, "audio_outputs", summary_dir, missing)
    plots = collect_paths(summary, "plots", summary_dir, missing)

    missing = [path for path in missing if not Path(path).exists()]
    if missing and not allow_missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Referenced report artifacts are missing:\n{formatted}")
    return audio, plots, missing


def collect_paths(
    summary: dict[str, Any],
    field: str,
    summary_dir: Path,
    missing: list[str],
) -> dict[str, Path]:
    value = summary.get(field)
    if not isinstance(value, dict):
        raise ValueError(f"summary field {field!r} must be an object")

    paths: dict[str, Path] = {}
    for key, path_value in value.items():
        path = resolve_artifact(path_value, summary_dir, f"{field}.{key}")
        paths[str(key)] = path
        if not path.exists():
            missing.append(str(path))
    return paths


def fmt_number(value: object, digits: int = 4) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return html.escape(str(value))


def render_metric_table(metrics: object) -> str:
    if not isinstance(metrics, dict):
        raise ValueError("summary field 'aligned_test_metrics' must be an object")

    rows = []
    ordered_keys = [key for key in METRIC_LABELS if key in metrics]
    ordered_keys += sorted(key for key in metrics if key not in METRIC_LABELS)
    for key in ordered_keys:
        value = metrics[key]
        if not isinstance(value, dict):
            continue
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{html.escape(METRIC_LABELS.get(key, key))}</th>"
            f"<td>{fmt_number(value.get('mse'))}</td>"
            f"<td>{fmt_number(value.get('mae'))}</td>"
            f"<td>{html.escape(str(value.get('aligned_frames', '-')))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_audio_cards(audio: dict[str, Path], html_dir: Path, missing: list[str]) -> str:
    cards = []
    for key in sorted(audio):
        path = audio[key]
        label = display_label(key)
        missing_note = " missing" if str(path) in missing else ""
        cards.append(
            f"<article class=\"audio-card{missing_note}\">"
            f"<h3>{html.escape(label)}</h3>"
            f"<audio controls src=\"{html.escape(relative_href(path, html_dir))}\"></audio>"
            f"<p>{html.escape(path.name)}</p>"
            "</article>"
        )
    return "\n".join(cards)


def render_plot_figures(plots: dict[str, Path], html_dir: Path, missing: list[str]) -> str:
    figures = []
    for key in ["trajectories", "meanstd_comparison", "full_affine_heatmap"]:
        if key not in plots:
            continue
        path = plots[key]
        label = PLOT_LABELS.get(key, key.replace("_", " ").title())
        missing_note = " missing" if str(path) in missing else ""
        figures.append(
            f"<figure class=\"plot{missing_note}\">"
            f"<img src=\"{html.escape(relative_href(path, html_dir))}\" alt=\"{html.escape(label)}\">"
            f"<figcaption>{html.escape(label)}</figcaption>"
            "</figure>"
        )
    return "\n".join(figures)


def render_report(
    summary: dict[str, Any],
    summary_path: Path,
    audio: dict[str, Path],
    plots: dict[str, Path],
    html_path: Path,
    missing: list[str],
) -> str:
    html_dir = html_path.parent.resolve()
    metric_rows = render_metric_table(summary.get("aligned_test_metrics"))
    audio_cards = render_audio_cards(audio, html_dir, missing)
    plot_figures = render_plot_figures(plots, html_dir, missing)
    summary_href = html.escape(relative_href(summary_path, html_dir))
    title = f"ARTI-6 + LinearVC tiny floor: {summary.get('test_utterance_id', 'unknown')}"

    missing_block = ""
    if missing:
        items = "\n".join(f"<li>{html.escape(path)}</li>" for path in missing)
        missing_block = f"<section class=\"warning\"><h2>Missing artifacts</h2><ul>{items}</ul></section>"

    train_ids = summary.get("train_utterance_ids", [])
    if isinstance(train_ids, list):
        train_ids_text = ", ".join(str(item) for item in train_ids)
    else:
        train_ids_text = str(train_ids)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6a71;
      --line: #d8dee3;
      --panel: #f7f8f8;
      --accent: #1f6f78;
      --warn: #8b3e13;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      color: var(--ink);
      background: #ffffff;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(2rem, 5vw, 3.25rem);
      line-height: 1.08;
      letter-spacing: 0;
    }}
    h2 {{ margin: 32px 0 12px; font-size: 1.35rem; }}
    h3 {{ margin: 0 0 10px; font-size: 1rem; }}
    p {{ margin: 0 0 12px; }}
    .meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
      margin-top: 18px;
    }}
    .meta div, .audio-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--panel);
    }}
    .meta strong {{
      display: block;
      color: var(--muted);
      font-size: .82rem;
      font-weight: 650;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      border: 1px solid var(--line);
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: right;
    }}
    th:first-child, td:first-child {{ text-align: left; }}
    thead th {{ background: var(--panel); color: var(--muted); }}
    .audio-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }}
    audio {{ width: 100%; }}
    .audio-card p {{ color: var(--muted); font-size: .85rem; overflow-wrap: anywhere; }}
    .plots {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 18px;
    }}
    figure {{ margin: 0; }}
    img {{
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    figcaption {{ margin-top: 8px; color: var(--muted); }}
    .notice, .warning {{
      border-left: 4px solid var(--accent);
      background: var(--panel);
      padding: 12px 14px;
    }}
    .warning {{ border-left-color: var(--warn); }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>ARTI-6 + LinearVC tiny floor</h1>
    <p>This local report packages the first held-out tiny experiment for listening and inspection. It is a floor check, not a scientific claim of conversion quality.</p>
    <div class="meta">
      <div><strong>Test utterance</strong>{html.escape(str(summary.get("test_utterance_id", "-")))}</div>
      <div><strong>Train utterances</strong>{html.escape(train_ids_text)}</div>
      <div><strong>Train frames</strong>{html.escape(str(summary.get("train_frames", "-")))}</div>
      <div><strong>Device</strong>{html.escape(str(summary.get("cuda_device_name") or summary.get("device", "-")))}</div>
      <div><strong>Alignment</strong>{html.escape(str(summary.get("alignment_policy", "-")))}</div>
      <div><strong>Summary</strong><a href="{summary_href}">summary.json</a></div>
    </div>
  </header>

  <section class="notice">
    <p>The comparison uses same-prompt CMU ARCTIC pairs and truncates paired trajectories to their shared minimum length. Lower held-out MSE/MAE means the transformed 6D articulatory trajectory is numerically closer to the target trajectory under this crude alignment.</p>
  </section>

  <section>
    <h2>Aligned Test Metrics</h2>
    <table>
      <thead><tr><th>Condition</th><th>MSE</th><th>MAE</th><th>Aligned frames</th></tr></thead>
      <tbody>
        {metric_rows}
      </tbody>
    </table>
  </section>

  <section>
    <h2>Audio Conditions</h2>
    <div class="audio-grid">
      {audio_cards}
    </div>
  </section>

  <section>
    <h2>Plots</h2>
    <div class="plots">
      {plot_figures}
    </div>
  </section>

  <section class="notice">
    <h2>Current Interpretation Boundary</h2>
    <p>The full affine transform has the best held-out numerical fit in this tiny run, followed by the diagonal affine transform. The plots still need human inspection, and the alignment is intentionally primitive, so this result only justifies scaling to the next controlled experiment.</p>
  </section>

  {missing_block}
</main>
</body>
</html>
"""


def default_bundle_path(summary_dir: Path) -> Path:
    return summary_dir / f"{summary_dir.name}_report.zip"


def require_relative_member(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(
            f"{path} is outside {root}; use the default output location when building a zip bundle"
        ) from exc


def write_bundle(
    bundle_path: Path,
    html_path: Path,
    summary_path: Path,
    audio: dict[str, Path],
    plots: dict[str, Path],
) -> None:
    root = html_path.parent.resolve()
    members = [html_path.resolve(), summary_path.resolve()]
    members.extend(path.resolve() for path in audio.values())
    members.extend(path.resolve() for path in plots.values())

    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(bundle_path, "w", compression=ZIP_DEFLATED) as bundle:
        seen: set[str] = set()
        for path in members:
            arcname = require_relative_member(path, root)
            if arcname in seen:
                continue
            bundle.write(path, arcname)
            seen.add(arcname)


def main() -> None:
    args = parse_args()
    summary_path = args.summary.resolve()
    summary_dir = summary_path.parent
    html_path = (args.output or summary_dir / "index.html").resolve()

    summary = load_summary(summary_path)
    audio, plots, missing = validate_artifacts(summary, summary_dir, args.allow_missing)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(
        render_report(summary, summary_path, audio, plots, html_path, missing),
        encoding="utf-8",
    )
    print(html_path)
    if args.bundle_zip is not None:
        bundle_path = (
            default_bundle_path(summary_dir)
            if args.bundle_zip == Path("__default__")
            else args.bundle_zip.resolve()
        )
        write_bundle(bundle_path, html_path, summary_path, audio, plots)
        print(bundle_path)


if __name__ == "__main__":
    main()
