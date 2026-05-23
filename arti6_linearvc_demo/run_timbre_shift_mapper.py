#!/usr/bin/env python3
"""Run a small latent timbre-shift mapper demo over paired audio."""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import sys
from pathlib import Path
from time import perf_counter
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

import matplotlib
import numpy as np
import soundfile as sf
import torch
import torch.nn.functional as F

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTI6_ROOT = REPO_ROOT / "external" / "arti-6"
sys.path.insert(0, str(ARTI6_ROOT / "arti6"))

from arti6 import ARTI6  # noqa: E402


REQUIRED_MANIFEST_COLUMNS = {"utterance_id", "source_wav", "target_wav"}


class MicroMapper(torch.nn.Module):
    """Small residual MLP that maps a base speaker embedding to a shifted embedding."""

    def __init__(self, embedding_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(embedding_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, embedding_dim),
        )

    def forward(self, embedding: torch.Tensor) -> torch.Tensor:
        shifted = embedding + self.net(embedding)
        return F.normalize(shifted, p=2, dim=-1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a tiny latent timbre-shift mapper and compare it with a "
            "difference-of-means steering vector."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--train-count", type=int, required=True)
    parser.add_argument(
        "--test-index",
        type=int,
        required=True,
        help="Row index in the manifest used for held-out synthesis/evaluation.",
    )
    parser.add_argument(
        "--slider-alpha",
        type=float,
        default=1.0,
        help="Strength for Route A: source_embedding + alpha * mean_delta.",
    )
    parser.add_argument(
        "--sweep-slider-alpha",
        dest="sweep_slider_alphas",
        type=float,
        action="append",
        default=[],
        help="Also evaluate Route A at this alpha in summary metrics. May be repeated.",
    )
    parser.add_argument(
        "--synthesize-sweep-audio",
        action="store_true",
        help="Also synthesize wav files for every Route A alpha in the slider sweep.",
    )
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--allow-train-test-overlap",
        action="store_true",
        help="Allow the held-out test row to also appear in the first train-count rows.",
    )
    parser.add_argument(
        "--bundle-zip",
        type=Path,
        nargs="?",
        const=Path("__default__"),
        default=None,
        help=(
            "Also write a portable zip bundle containing index.html, summary.json, "
            "audio, plots, arrays, and model state. Defaults to "
            "<output-dir>/<output-dir-name>_report.zip."
        ),
    )
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a CSV header")
        missing = REQUIRED_MANIFEST_COLUMNS - set(reader.fieldnames)
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required column(s): {missing_text}")
        return list(reader)


def ensure_clean_dirs(output_dir: Path) -> dict[str, Path]:
    paths = {
        "audio": output_dir / "audio",
        "arrays": output_dir / "arrays",
        "plots": output_dir / "plots",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
    return paths


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def normalize_np(array: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(array, axis=-1, keepdims=True)
    if np.any(norm == 0):
        raise ValueError("cannot normalize a zero embedding")
    return array / norm


def tensor_summary(array: np.ndarray) -> dict[str, object]:
    return {
        "shape": list(array.shape),
        "min": float(np.min(array)),
        "max": float(np.max(array)),
        "mean": float(np.mean(array)),
        "std": float(np.std(array)),
        "has_nan": bool(np.isnan(array).any()),
        "has_inf": bool(np.isinf(array).any()),
    }


def embedding_metrics(prediction: np.ndarray, target: np.ndarray) -> dict[str, float]:
    prediction = prediction.reshape(-1)
    target = target.reshape(-1)
    cosine = float(np.dot(prediction, target) / (np.linalg.norm(prediction) * np.linalg.norm(target)))
    error = prediction - target
    return {
        "mse": float(np.mean(error**2)),
        "mae": float(np.mean(np.abs(error))),
        "l2_distance": float(np.linalg.norm(error)),
        "cosine": cosine,
    }


def extract_pair(model: ARTI6, row: dict[str, str]) -> dict[str, object]:
    source = model.invert(wav_path=row["source_wav"])
    target = model.invert(wav_path=row["target_wav"])
    source_spk = source["spk_emb"].detach().cpu().numpy().reshape(-1)
    target_spk = target["spk_emb"].detach().cpu().numpy().reshape(-1)
    return {
        "utterance_id": row["utterance_id"],
        "source_wav": row["source_wav"],
        "target_wav": row["target_wav"],
        "speaker_id": row.get("speaker_id", ""),
        "source_domain": row.get("source_domain", row.get("source_speaker", "")),
        "target_domain": row.get("target_domain", row.get("target_speaker", "")),
        "source_speaker": row.get("source_speaker", ""),
        "target_speaker": row.get("target_speaker", ""),
        "source_arti": source["arti_feats"].detach().cpu().numpy()[0],
        "target_arti": target["arti_feats"].detach().cpu().numpy()[0],
        "source_spk_emb": normalize_np(source_spk),
        "target_spk_emb": normalize_np(target_spk),
    }


def fit_difference_of_means(
    source_embeddings: np.ndarray,
    target_embeddings: np.ndarray,
) -> dict[str, np.ndarray]:
    source_mean = source_embeddings.mean(axis=0)
    target_mean = target_embeddings.mean(axis=0)
    return {
        "source_mean": normalize_np(source_mean),
        "target_mean": normalize_np(target_mean),
        "delta": target_mean - source_mean,
    }


def apply_difference_of_means(
    source_embedding: np.ndarray,
    params: dict[str, np.ndarray],
    alpha: float,
) -> np.ndarray:
    return normalize_np(source_embedding + alpha * params["delta"])


def train_micro_mapper(
    source_embeddings: np.ndarray,
    target_embeddings: np.ndarray,
    hidden_dim: int,
    epochs: int,
    learning_rate: float,
    device: str,
) -> tuple[MicroMapper, list[dict[str, float]]]:
    if epochs < 1:
        raise ValueError("epochs must be >= 1")
    model = MicroMapper(source_embeddings.shape[1], hidden_dim).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    source = torch.from_numpy(source_embeddings).to(device=device, dtype=torch.float32)
    target = torch.from_numpy(target_embeddings).to(device=device, dtype=torch.float32)
    history: list[dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        prediction = model(source)
        mse = F.mse_loss(prediction, target)
        cosine_loss = 1.0 - F.cosine_similarity(prediction, target, dim=-1).mean()
        loss = mse + 0.1 * cosine_loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
        optimizer.step()

        if epoch == 1 or epoch == epochs or epoch % max(1, epochs // 10) == 0:
            history.append(
                {
                    "epoch": float(epoch),
                    "loss": float(loss.detach().cpu()),
                    "mse": float(mse.detach().cpu()),
                    "cosine_loss": float(cosine_loss.detach().cpu()),
                }
            )

    return model, history


def predict_micro_mapper(
    model: MicroMapper,
    source_embedding: np.ndarray,
    device: str,
) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        source = torch.from_numpy(source_embedding[None, :]).to(device=device, dtype=torch.float32)
        prediction = model(source).detach().cpu().numpy()[0]
    return normalize_np(prediction)


def torchify_arti(features: np.ndarray, device: str) -> torch.Tensor:
    return torch.from_numpy(features).unsqueeze(0).to(device=device, dtype=torch.float32)


def torchify_embedding(embedding: np.ndarray, device: str) -> torch.Tensor:
    return torch.from_numpy(embedding).unsqueeze(0).to(device=device, dtype=torch.float32)


def alpha_tag(alpha: object) -> str:
    return f"{float(alpha):.2f}".replace(".", "p").replace("-", "neg")


def save_audio_conditions(
    model: ARTI6,
    test_pair: dict[str, object],
    shifted_embeddings: dict[str, np.ndarray],
    audio_dir: Path,
    route_a_sweep_embeddings: dict[str, np.ndarray] | None = None,
) -> dict[str, str]:
    source_arti = test_pair["source_arti"]
    target_arti = test_pair["target_arti"]
    source_spk = test_pair["source_spk_emb"]
    target_spk = test_pair["target_spk_emb"]
    assert isinstance(source_arti, np.ndarray)
    assert isinstance(target_arti, np.ndarray)
    assert isinstance(source_spk, np.ndarray)
    assert isinstance(target_spk, np.ndarray)

    conditions = {
        "01_source_reconstruction": (source_arti, source_spk),
        "02_target_reconstruction": (target_arti, target_spk),
        "03_oracle_source_arti_plus_target_embedding": (source_arti, target_spk),
        "04_route_a_slider_source_arti_plus_shifted_embedding": (
            source_arti,
            shifted_embeddings["route_a_slider"],
        ),
        "05_route_b_micro_mapper_source_arti_plus_shifted_embedding": (
            source_arti,
            shifted_embeddings["route_b_micro_mapper"],
        ),
    }
    if route_a_sweep_embeddings:
        for index, alpha in enumerate(sorted(route_a_sweep_embeddings, key=float), start=6):
            tag = alpha_tag(alpha)
            conditions[f"{index:02d}_route_a_alpha_{tag}_source_arti_plus_shifted_embedding"] = (
                source_arti,
                route_a_sweep_embeddings[alpha],
            )

    outputs: dict[str, str] = {}
    for name, (features, embedding) in conditions.items():
        audio = model.synthesize(
            torchify_arti(features, model.device),
            torchify_embedding(embedding, model.device),
        )
        path = audio_dir / f"{name}.wav"
        sf.write(path, audio, 16000)
        outputs[name] = str(path)
    return outputs


def pca_2d(points: np.ndarray) -> np.ndarray:
    centered = points - points.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    return centered @ vt[:2].T


def plot_embedding_geometry(
    train_source: np.ndarray,
    train_target: np.ndarray,
    test_points: dict[str, np.ndarray],
    path: Path,
) -> None:
    labels: list[str] = []
    groups: list[str] = []
    points: list[np.ndarray] = []
    for index, embedding in enumerate(train_source, start=1):
        labels.append(f"train source {index}")
        groups.append("train source")
        points.append(embedding)
    for index, embedding in enumerate(train_target, start=1):
        labels.append(f"train target {index}")
        groups.append("train target")
        points.append(embedding)
    for label, embedding in test_points.items():
        labels.append(label)
        groups.append(label)
        points.append(embedding)

    coords = pca_2d(np.stack(points, axis=0))
    colors = {
        "train source": "#4a6572",
        "train target": "#d05d3b",
        "test source": "#111111",
        "test target": "#b3261e",
        "Route A slider": "#1f6f78",
        "Route B micro-mapper": "#6f5aa7",
    }

    fig, ax = plt.subplots(figsize=(8, 6))
    for group in sorted(set(groups)):
        indices = [idx for idx, value in enumerate(groups) if value == group]
        ax.scatter(
            coords[indices, 0],
            coords[indices, 1],
            label=group,
            color=colors.get(group, "#777777"),
            s=54 if group.startswith("test") or group.startswith("Route") else 34,
            alpha=0.92,
        )
    for label, (x_coord, y_coord) in zip(labels, coords):
        if label.startswith("test") or label.startswith("Route"):
            ax.annotate(label, (x_coord, y_coord), xytext=(5, 4), textcoords="offset points")
    ax.set_title("Speaker embedding shift geometry (PCA)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_training_history(history: list[dict[str, float]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    epochs = [entry["epoch"] for entry in history]
    losses = [entry["loss"] for entry in history]
    ax.plot(epochs, losses, marker="o", linewidth=1.4)
    ax.set_title("Micro-Mapper training loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def relative_href(path: Path, html_dir: Path) -> str:
    return Path(os.path.relpath(path.resolve(), html_dir.resolve())).as_posix()


def fmt_number(value: object, digits: int = 4) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return html.escape(str(value))


def render_metric_rows(metrics: dict[str, Any]) -> str:
    labels = {
        "source_embedding": "Unshifted source embedding",
        "route_a_slider": "Route A: difference-of-means slider",
        "route_b_micro_mapper": "Route B: Micro-Mapper",
        "target_embedding": "Target embedding oracle",
    }
    rows = []
    for key in ["source_embedding", "route_a_slider", "route_b_micro_mapper", "target_embedding"]:
        value = metrics.get(key, {})
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{html.escape(labels[key])}</th>"
            f"<td>{fmt_number(value.get('mse'))}</td>"
            f"<td>{fmt_number(value.get('l2_distance'))}</td>"
            f"<td>{fmt_number(value.get('cosine'))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_audio_cards(audio: dict[str, str], html_dir: Path) -> str:
    labels = {
        "01_source_reconstruction": "Source reconstruction",
        "02_target_reconstruction": "Target reconstruction",
        "03_oracle_source_arti_plus_target_embedding": "Oracle: source articulation + target embedding",
        "04_route_a_slider_source_arti_plus_shifted_embedding": "Route A: slider-shifted embedding",
        "05_route_b_micro_mapper_source_arti_plus_shifted_embedding": "Route B: Micro-Mapper shifted embedding",
    }
    cards = []
    for key in sorted(audio):
        path = Path(audio[key])
        label = labels.get(key, key)
        if "_route_a_alpha_" in key:
            alpha = key.split("_route_a_alpha_", 1)[1].split("_source_arti", 1)[0]
            label = f"Route A slider alpha={alpha.replace('p', '.')}"
        cards.append(
            "<article class=\"audio-card\">"
            f"<h3>{html.escape(label)}</h3>"
            f"<audio controls src=\"{html.escape(relative_href(path, html_dir))}\"></audio>"
            f"<p>{html.escape(path.name)}</p>"
            "</article>"
        )
    return "\n".join(cards)


def render_report(summary: dict[str, Any], summary_path: Path, html_path: Path) -> str:
    html_dir = html_path.parent.resolve()
    audio_cards = render_audio_cards(summary["audio_outputs"], html_dir)
    metric_rows = render_metric_rows(summary["embedding_metrics_to_target"])
    geometry = Path(summary["plots"]["embedding_geometry"])
    training = Path(summary["plots"]["training_loss"])
    train_ids = ", ".join(summary["train_utterance_ids"])
    verdict = summary["feasibility_verdict"]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cross-Domain Timbre Shift Demo</title>
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
      font-size: clamp(2rem, 5vw, 3.1rem);
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
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    thead th {{ background: var(--panel); }}
    .audio-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 12px;
    }}
    audio {{ width: 100%; }}
    .plots {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }}
    figure {{ margin: 0; }}
    img {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    figcaption {{ color: var(--muted); font-size: .9rem; }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>Cross-Domain Timbre Shift Demo</h1>
    <p>Route A uses a difference-of-means steering vector. Route B trains a tiny residual MLP over ARTI-6 ECAPA speaker embeddings and feeds shifted embeddings into the frozen ARTI-6 synthesizer.</p>
    <div class="meta">
      <div><strong>Train utterances</strong>{html.escape(train_ids)}</div>
      <div><strong>Test utterance</strong>{html.escape(str(summary["test_utterance_id"]))}</div>
      <div><strong>Device</strong>{html.escape(str(summary["device"]))}</div>
      <div><strong>Verdict</strong>{html.escape(str(verdict["best_method"]))} improved cosine by {fmt_number(verdict["best_cosine_gain"])}</div>
    </div>
  </header>

  <section>
    <h2>Embedding Metrics To Target</h2>
    <table>
      <thead><tr><th>Condition</th><th>MSE</th><th>L2 distance</th><th>Cosine</th></tr></thead>
      <tbody>{metric_rows}</tbody>
    </table>
  </section>

  <section>
    <h2>Comparative Audio</h2>
    <div class="audio-grid">{audio_cards}</div>
  </section>

  <section>
    <h2>Diagnostics</h2>
    <div class="plots">
      <figure>
        <img src="{html.escape(relative_href(geometry, html_dir))}" alt="Embedding geometry PCA plot">
        <figcaption>Embedding geometry after PCA.</figcaption>
      </figure>
      <figure>
        <img src="{html.escape(relative_href(training, html_dir))}" alt="Micro-Mapper training loss plot">
        <figcaption>Micro-Mapper training loss.</figcaption>
      </figure>
    </div>
  </section>

  <p><a href="{html.escape(relative_href(summary_path, html_dir))}">summary.json</a></p>
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
    set_seed(args.seed)

    manifest = args.manifest.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dirs = ensure_clean_dirs(output_dir)

    rows = read_manifest(manifest)
    if args.train_count < 1:
        raise ValueError("train-count must be >= 1")
    if args.train_count > len(rows):
        raise ValueError("manifest does not contain enough rows for training")
    if args.test_index < 0 or args.test_index >= len(rows):
        raise ValueError("test-index is outside the manifest")
    if args.test_index < args.train_count and not args.allow_train_test_overlap:
        raise ValueError(
            "test-index is inside the training slice; choose a held-out row or pass "
            "--allow-train-test-overlap for a bookkeeping-only smoke run"
        )

    os.chdir(ARTI6_ROOT)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    started = perf_counter()
    model = ARTI6(device=device)
    model.load_model()
    model_load_s = perf_counter() - started

    extracted = [extract_pair(model, row) for row in rows[: max(args.train_count, args.test_index + 1)]]
    train_pairs = extracted[: args.train_count]
    test_pair = extracted[args.test_index]

    train_source = np.stack(
        [pair["source_spk_emb"] for pair in train_pairs if isinstance(pair["source_spk_emb"], np.ndarray)],
        axis=0,
    )
    train_target = np.stack(
        [pair["target_spk_emb"] for pair in train_pairs if isinstance(pair["target_spk_emb"], np.ndarray)],
        axis=0,
    )
    source_test = test_pair["source_spk_emb"]
    target_test = test_pair["target_spk_emb"]
    assert isinstance(source_test, np.ndarray)
    assert isinstance(target_test, np.ndarray)

    route_a_params = fit_difference_of_means(train_source, train_target)
    route_a_embedding = apply_difference_of_means(source_test, route_a_params, args.slider_alpha)
    sweep_alphas = sorted(set([0.0, args.slider_alpha, *args.sweep_slider_alphas]))
    route_a_sweep_embeddings = {
        str(alpha): apply_difference_of_means(source_test, route_a_params, alpha)
        for alpha in sweep_alphas
    }

    mapper_started = perf_counter()
    micro_mapper, training_history = train_micro_mapper(
        train_source,
        train_target,
        args.hidden_dim,
        args.epochs,
        args.learning_rate,
        device,
    )
    mapper_train_s = perf_counter() - mapper_started
    route_b_embedding = predict_micro_mapper(micro_mapper, source_test, device)

    shifted_embeddings = {
        "route_a_slider": route_a_embedding,
        "route_b_micro_mapper": route_b_embedding,
    }
    arrays = {
        "train_source_spk_emb": train_source,
        "train_target_spk_emb": train_target,
        "source_test_spk_emb": source_test,
        "target_test_spk_emb": target_test,
        "route_a_source_mean": route_a_params["source_mean"],
        "route_a_target_mean": route_a_params["target_mean"],
        "route_a_delta": route_a_params["delta"],
        "route_a_shifted_spk_emb": route_a_embedding,
        "route_b_shifted_spk_emb": route_b_embedding,
    }
    for alpha, embedding in route_a_sweep_embeddings.items():
        arrays[f"route_a_alpha_{alpha_tag(alpha)}_spk_emb"] = embedding
    for name, value in arrays.items():
        np.save(dirs["arrays"] / f"{name}.npy", value)
    torch.save(micro_mapper.state_dict(), dirs["arrays"] / "route_b_micro_mapper_state.pt")

    sweep_audio_embeddings = route_a_sweep_embeddings if args.synthesize_sweep_audio else None
    audio_outputs = save_audio_conditions(
        model,
        test_pair,
        shifted_embeddings,
        dirs["audio"],
        sweep_audio_embeddings,
    )
    plot_embedding_geometry(
        train_source,
        train_target,
        {
            "test source": source_test,
            "test target": target_test,
            "Route A slider": route_a_embedding,
            "Route B micro-mapper": route_b_embedding,
        },
        dirs["plots"] / "embedding_geometry.png",
    )
    plot_training_history(training_history, dirs["plots"] / "training_loss.png")

    metrics = {
        "source_embedding": embedding_metrics(source_test, target_test),
        "route_a_slider": embedding_metrics(route_a_embedding, target_test),
        "route_b_micro_mapper": embedding_metrics(route_b_embedding, target_test),
        "target_embedding": embedding_metrics(target_test, target_test),
    }
    route_a_alpha_sweep = {
        alpha: embedding_metrics(embedding, target_test)
        for alpha, embedding in route_a_sweep_embeddings.items()
    }
    source_cosine = metrics["source_embedding"]["cosine"]
    candidate_gains = {
        "route_a_slider": metrics["route_a_slider"]["cosine"] - source_cosine,
        "route_b_micro_mapper": metrics["route_b_micro_mapper"]["cosine"] - source_cosine,
    }
    best_method = max(candidate_gains, key=candidate_gains.get)
    feasibility_verdict = {
        "best_method": best_method,
        "best_cosine_gain": float(candidate_gains[best_method]),
        "route_a_improved_over_source": bool(candidate_gains["route_a_slider"] > 0),
        "route_b_improved_over_source": bool(candidate_gains["route_b_micro_mapper"] > 0),
        "note": (
            "This is a feasibility demo over ARTI-6 ECAPA speaker embeddings. "
            "A real cross-domain claim still needs same-speaker different-domain data."
        ),
    }

    summary = {
        "manifest": str(manifest),
        "device": device,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "model_load_s": round(model_load_s, 4),
        "micro_mapper_train_s": round(mapper_train_s, 4),
        "train_count": args.train_count,
        "test_index": args.test_index,
        "train_test_overlap": bool(args.test_index < args.train_count),
        "train_utterance_ids": [str(pair["utterance_id"]) for pair in train_pairs],
        "test_utterance_id": str(test_pair["utterance_id"]),
        "speaker_id": str(test_pair.get("speaker_id", "")),
        "source_domain": str(test_pair.get("source_domain", "")),
        "target_domain": str(test_pair.get("target_domain", "")),
        "embedding_extractor": "ARTI-6 ECAPA-TDNN speaker encoder",
        "decoder": "Frozen ARTI-6 articulatory synthesizer",
        "route_a": {
            "method": "difference_of_means",
            "slider_alpha": args.slider_alpha,
            "alpha_sweep": route_a_alpha_sweep,
            "sweep_audio_enabled": bool(args.synthesize_sweep_audio),
        },
        "route_b": {
            "method": "residual_mlp_micro_mapper",
            "epochs": args.epochs,
            "hidden_dim": args.hidden_dim,
            "learning_rate": args.learning_rate,
            "training_history": training_history,
        },
        "embedding_metrics_to_target": metrics,
        "tensor_summaries": {name: tensor_summary(value) for name, value in arrays.items()},
        "feasibility_verdict": feasibility_verdict,
        "audio_outputs": audio_outputs,
        "plots": {
            "embedding_geometry": str(dirs["plots"] / "embedding_geometry.png"),
            "training_loss": str(dirs["plots"] / "training_loss.png"),
        },
    }
    summary_path = output_dir / "summary.json"
    bundle_path = resolve_bundle_path(args.bundle_zip, output_dir)
    if bundle_path is not None:
        summary["report_zip"] = str(bundle_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    html_path = output_dir / "index.html"
    html_path.write_text(render_report(summary, summary_path, html_path))
    if bundle_path is not None:
        write_bundle(output_dir, bundle_path)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
