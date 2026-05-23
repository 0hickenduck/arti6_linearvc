#!/usr/bin/env python3
"""Build a static blind subjective-evaluation page for a timbre-shift demo."""

from __future__ import annotations

import argparse
import html
import json
import os
import random
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


DEFAULT_REFERENCE = "02_target_reconstruction"
DEFAULT_DIMENSIONS = [
    ("naturalness", "Naturalness"),
    ("target_domain_match", "Singing-likeness / target-domain match"),
    ("target_timbre_similarity", "Timbre similarity to target reference"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a blind subjective evaluation HTML page from a timbre-shift summary."
    )
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output HTML path. Defaults to subjective_eval.html beside summary.json.",
    )
    parser.add_argument(
        "--reference-condition",
        default=DEFAULT_REFERENCE,
        help="Condition key used as the visible target reference.",
    )
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument(
        "--bundle-zip",
        type=Path,
        nargs="?",
        const=Path("__default__"),
        default=None,
        help="Also write/update a portable zip bundle for the full output directory.",
    )
    return parser.parse_args()


def load_summary(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def as_audio_outputs(summary: dict[str, Any]) -> dict[str, str]:
    audio = summary.get("audio_outputs")
    if not isinstance(audio, dict):
        raise ValueError("summary field 'audio_outputs' must be an object")
    return {str(key): str(value) for key, value in audio.items()}


def relative_href(path: Path, html_dir: Path) -> str:
    return Path(os.path.relpath(path.resolve(), html_dir.resolve())).as_posix()


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


def make_eval_plan(
    audio: dict[str, str],
    reference_condition: str,
    seed: int,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    if reference_condition not in audio:
        raise ValueError(f"reference condition {reference_condition!r} is not in audio_outputs")

    candidates = [
        key
        for key in audio
        if key != reference_condition
    ]
    rng = random.Random(seed)
    rng.shuffle(candidates)
    samples = [
        {
            "sample_id": f"S{index:02d}",
            "condition": key,
            "audio_path": audio[key],
        }
        for index, key in enumerate(candidates, start=1)
    ]
    reference = {
        "condition": reference_condition,
        "audio_path": audio[reference_condition],
    }
    return reference, samples


def render_scale(sample_id: str, dimension_key: str) -> str:
    name = f"{sample_id}_{dimension_key}"
    options = []
    for value in range(1, 6):
        options.append(
            "<label>"
            f"<input type=\"radio\" name=\"{html.escape(name)}\" value=\"{value}\">"
            f"<span>{value}</span>"
            "</label>"
        )
    return "<div class=\"scale\">" + "".join(options) + "</div>"


def render_samples(samples: list[dict[str, str]], html_dir: Path) -> str:
    cards = []
    for sample in samples:
        sample_id = sample["sample_id"]
        path = Path(sample["audio_path"])
        ratings = []
        for key, label in DEFAULT_DIMENSIONS:
            ratings.append(
                "<div class=\"rating-row\">"
                f"<span>{html.escape(label)}</span>"
                f"{render_scale(sample_id, key)}"
                "</div>"
            )
        cards.append(
            f"<article class=\"sample\" data-sample-id=\"{html.escape(sample_id)}\">"
            f"<h3>{html.escape(sample_id)}</h3>"
            f"<audio controls preload=\"metadata\" src=\"{html.escape(relative_href(path, html_dir))}\"></audio>"
            + "\n".join(ratings)
            + f"<textarea id=\"{html.escape(sample_id)}_notes\" placeholder=\"Notes\"></textarea>"
            "</article>"
        )
    return "\n".join(cards)


def render_page(
    summary: dict[str, Any],
    summary_path: Path,
    html_path: Path,
    reference: dict[str, str],
    samples: list[dict[str, str]],
) -> str:
    html_dir = html_path.parent.resolve()
    reference_href = relative_href(Path(reference["audio_path"]), html_dir)
    samples_html = render_samples(samples, html_dir)
    dimensions_json = json.dumps([key for key, _ in DEFAULT_DIMENSIONS])
    sample_ids_json = json.dumps([sample["sample_id"] for sample in samples])
    key_href = relative_href(html_path.with_name("subjective_eval_key.json"), html_dir)
    summary_href = relative_href(summary_path, html_dir)
    title = "Blind Subjective Evaluation"
    speaker = summary.get("speaker_id") or summary.get("test_utterance_id", "unknown")
    source_domain = summary.get("source_domain", "source")
    target_domain = summary.get("target_domain", "target")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6a71;
      --line: #d8dee3;
      --panel: #f7f8f8;
      --accent: #1f6f78;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
      line-height: 1.5;
    }}
    main {{
      width: min(960px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 1.25rem; }}
    h3 {{ margin: 0 0 10px; font-size: 1.05rem; }}
    p {{ margin: 0 0 12px; }}
    .reference, .sample {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 14px;
      margin-bottom: 14px;
    }}
    audio {{ width: 100%; }}
    .rating-row {{
      display: grid;
      grid-template-columns: minmax(180px, 1fr) auto;
      gap: 12px;
      align-items: center;
      padding: 10px 0;
      border-top: 1px solid var(--line);
    }}
    .scale {{
      display: grid;
      grid-template-columns: repeat(5, 38px);
      gap: 6px;
    }}
    .scale label {{
      display: block;
      text-align: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      cursor: pointer;
    }}
    .scale input {{ position: absolute; opacity: 0; pointer-events: none; }}
    .scale span {{ display: block; padding: 7px 0; }}
    .scale input:checked + span {{
      background: var(--accent);
      color: #ffffff;
      border-radius: 7px;
    }}
    textarea {{
      width: 100%;
      min-height: 62px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px;
      font: inherit;
    }}
    button {{
      appearance: none;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: #ffffff;
      padding: 10px 14px;
      font-weight: 650;
      cursor: pointer;
    }}
    a {{ color: var(--accent); }}
    .muted {{ color: var(--muted); }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{title}</h1>
    <p>Speaker: {html.escape(str(speaker))}. Task: {html.escape(str(source_domain))} to {html.escape(str(target_domain))}.</p>
    <p class="muted">Rate each anonymized sample from 1 to 5. Use the target reference for timbre and domain comparison.</p>
  </header>

  <section class="reference">
    <h2>Target Reference</h2>
    <audio controls preload="metadata" src="{html.escape(reference_href)}"></audio>
  </section>

  <section>
    <h2>Blind Samples</h2>
    {samples_html}
  </section>

  <button type="button" id="download">Download responses JSON</button>
  <p class="muted">Condition key for analysis: <a href="{html.escape(key_href)}">subjective_eval_key.json</a>. Demo summary: <a href="{html.escape(summary_href)}">summary.json</a>.</p>
</main>
<script>
const sampleIds = {sample_ids_json};
const dimensions = {dimensions_json};
document.getElementById("download").addEventListener("click", () => {{
  const responses = {{
    created_at: new Date().toISOString(),
    summary: "{html.escape(summary_path.name)}",
    ratings: {{}}
  }};
  for (const sampleId of sampleIds) {{
    responses.ratings[sampleId] = {{ notes: document.getElementById(sampleId + "_notes").value }};
    for (const dimension of dimensions) {{
      const selected = document.querySelector(`input[name="${{sampleId}}_${{dimension}}"]:checked`);
      responses.ratings[sampleId][dimension] = selected ? Number(selected.value) : null;
    }}
  }}
  const blob = new Blob([JSON.stringify(responses, null, 2)], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "subjective_eval_response.json";
  link.click();
  URL.revokeObjectURL(url);
}});
</script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    summary_path = args.summary.resolve()
    summary_dir = summary_path.parent
    html_path = (args.output or summary_dir / "subjective_eval.html").resolve()
    summary = load_summary(summary_path)
    audio = as_audio_outputs(summary)
    reference, samples = make_eval_plan(audio, args.reference_condition, args.seed)

    key = {
        "reference": reference,
        "samples": samples,
        "dimensions": [{"key": key, "label": label, "scale": [1, 5]} for key, label in DEFAULT_DIMENSIONS],
        "scale_meaning": {
            "1": "poor / does not match",
            "5": "excellent / strongly matches",
        },
    }
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_page(summary, summary_path, html_path, reference, samples), encoding="utf-8")
    html_path.with_name("subjective_eval_key.json").write_text(
        json.dumps(key, indent=2) + "\n",
        encoding="utf-8",
    )

    bundle_path = resolve_bundle_path(args.bundle_zip, summary_dir)
    if bundle_path is not None:
        summary["subjective_eval"] = {
            "html": str(html_path),
            "key": str(html_path.with_name("subjective_eval_key.json")),
            "dimensions": key["dimensions"],
        }
        summary["report_zip"] = str(bundle_path)
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        write_bundle(summary_dir, bundle_path)
    print(html_path)
    if bundle_path is not None:
        print(bundle_path)


if __name__ == "__main__":
    main()
