#!/usr/bin/env python3
"""Run the first tiny ARTI-6 + LinearVC floor experiment."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from time import perf_counter

import matplotlib
import numpy as np
import soundfile as sf
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTI6_ROOT = REPO_ROOT / "external" / "arti-6"
sys.path.insert(0, str(ARTI6_ROOT / "arti6"))

from arti6 import ARTI6  # noqa: E402


ROI_NAMES = ["LA", "TT", "TB", "VL", "TR", "LX"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a tiny LinearVC floor over ARTI-6 articulatory features."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--train-count", type=int, required=True)
    parser.add_argument(
        "--test-index",
        type=int,
        required=True,
        help="Row index in the manifest used for synthesis/evaluation outputs.",
    )
    parser.add_argument(
        "--ridge-lambda",
        dest="ridge_lambdas",
        type=float,
        action="append",
        default=[],
        help="Add a ridge-regularized full affine map with this lambda. May be repeated.",
    )
    parser.add_argument(
        "--alpha",
        dest="alphas",
        type=float,
        action="append",
        default=[],
        help=(
            "Add pure residual-strength variants source + alpha * (transform - source). "
            "May be repeated."
        ),
    )
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


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


def regression_metrics(prediction: np.ndarray, target: np.ndarray) -> dict[str, float]:
    shared = min(len(prediction), len(target))
    error = prediction[:shared] - target[:shared]
    return {
        "aligned_frames": int(shared),
        "mse": float(np.mean(error**2)),
        "mae": float(np.mean(np.abs(error))),
    }


def extract_pair(model: ARTI6, row: dict[str, str]) -> dict[str, object]:
    source = model.invert(wav_path=row["source_wav"])
    target = model.invert(wav_path=row["target_wav"])
    return {
        "utterance_id": row["utterance_id"],
        "source_arti": source["arti_feats"].detach().cpu().numpy()[0],
        "target_arti": target["arti_feats"].detach().cpu().numpy()[0],
        "source_spk_emb": source["spk_emb"].detach().cpu().numpy(),
        "target_spk_emb": target["spk_emb"].detach().cpu().numpy(),
    }


def aligned_frames(pair: dict[str, object]) -> tuple[np.ndarray, np.ndarray]:
    source = pair["source_arti"]
    target = pair["target_arti"]
    assert isinstance(source, np.ndarray)
    assert isinstance(target, np.ndarray)
    shared = min(len(source), len(target))
    return source[:shared], target[:shared]


def fit_meanstd(source_frames: np.ndarray, target_frames: np.ndarray) -> dict[str, np.ndarray]:
    eps = 1e-6
    return {
        "source_mean": source_frames.mean(axis=0),
        "source_std": source_frames.std(axis=0) + eps,
        "target_mean": target_frames.mean(axis=0),
        "target_std": target_frames.std(axis=0) + eps,
    }


def transform_meanstd(features: np.ndarray, params: dict[str, np.ndarray]) -> np.ndarray:
    z = (features - params["source_mean"]) / params["source_std"]
    return z * params["target_std"] + params["target_mean"]


def fit_diag_affine(source_frames: np.ndarray, target_frames: np.ndarray) -> dict[str, np.ndarray]:
    scales = []
    biases = []
    design = np.stack([source_frames, np.ones_like(source_frames)], axis=-1)
    for dim in range(source_frames.shape[1]):
        coef, *_ = np.linalg.lstsq(design[:, dim, :], target_frames[:, dim], rcond=None)
        scales.append(coef[0])
        biases.append(coef[1])
    return {"scale": np.asarray(scales), "bias": np.asarray(biases)}


def transform_diag_affine(features: np.ndarray, params: dict[str, np.ndarray]) -> np.ndarray:
    return features * params["scale"] + params["bias"]


def fit_full_affine(source_frames: np.ndarray, target_frames: np.ndarray) -> dict[str, np.ndarray]:
    source_aug = np.concatenate(
        [source_frames, np.ones((source_frames.shape[0], 1), dtype=source_frames.dtype)],
        axis=1,
    )
    coef, *_ = np.linalg.lstsq(source_aug, target_frames, rcond=None)
    return {"weight": coef[:6, :], "bias": coef[6, :]}


def fit_ridge_full_affine(
    source_frames: np.ndarray,
    target_frames: np.ndarray,
    penalty: float,
) -> dict[str, np.ndarray]:
    if penalty < 0:
        raise ValueError("ridge lambda must be non-negative")
    source_aug = np.concatenate(
        [source_frames, np.ones((source_frames.shape[0], 1), dtype=source_frames.dtype)],
        axis=1,
    )
    regularizer = np.eye(source_aug.shape[1], dtype=source_aug.dtype) * penalty
    regularizer[-1, -1] = 0.0
    coef = np.linalg.solve(source_aug.T @ source_aug + regularizer, source_aug.T @ target_frames)
    return {"weight": coef[:6, :], "bias": coef[6, :], "lambda": np.asarray(penalty)}


def transform_full_affine(features: np.ndarray, params: dict[str, np.ndarray]) -> np.ndarray:
    return features @ params["weight"] + params["bias"]


def transform_residual_alpha(source: np.ndarray, transformed: np.ndarray, alpha: float) -> np.ndarray:
    return source + alpha * (transformed - source)


def normalized_average_embedding(embeddings: list[np.ndarray]) -> np.ndarray:
    stacked = np.concatenate(embeddings, axis=0)
    average = stacked.mean(axis=0, keepdims=True)
    norm = np.linalg.norm(average, axis=1, keepdims=True)
    if np.any(norm == 0):
        raise ValueError("cannot normalize a zero speaker embedding")
    return average / norm


def torchify(features: np.ndarray, device: str) -> torch.Tensor:
    return torch.from_numpy(features).unsqueeze(0).to(device=device, dtype=torch.float32)


def save_audio_conditions(
    model: ARTI6,
    pair: dict[str, object],
    transformed: dict[str, np.ndarray],
    average_spk: np.ndarray,
    ridge_names: list[str],
    alpha_names: list[str],
    audio_dir: Path,
) -> dict[str, str]:
    source_arti = pair["source_arti"]
    target_arti = pair["target_arti"]
    source_spk = pair["source_spk_emb"]
    target_spk = pair["target_spk_emb"]
    assert isinstance(source_arti, np.ndarray)
    assert isinstance(target_arti, np.ndarray)
    assert isinstance(source_spk, np.ndarray)
    assert isinstance(target_spk, np.ndarray)

    conditions = {
        "01_source_reconstruction": (source_arti, source_spk),
        "02_target_reconstruction": (target_arti, target_spk),
        "03_embedding_only_vc": (source_arti, target_spk),
        "04_oracle_target_arti_plus_source_spk": (target_arti, source_spk),
        "05_source_arti_plus_average_spk": (source_arti, average_spk),
        "06_target_arti_plus_average_spk": (target_arti, average_spk),
        "07_pure_meanstd_transform_plus_source_spk": (transformed["meanstd"], source_spk),
        "08_pure_diag_affine_transform_plus_source_spk": (transformed["diag_affine"], source_spk),
        "09_pure_full_affine_transform_plus_source_spk": (transformed["full_affine"], source_spk),
        "10_average_meanstd_transform_plus_average_spk": (transformed["meanstd"], average_spk),
        "11_average_diag_affine_transform_plus_average_spk": (transformed["diag_affine"], average_spk),
        "12_average_full_affine_transform_plus_average_spk": (transformed["full_affine"], average_spk),
        "13_hybrid_meanstd_transform_plus_target_spk": (transformed["meanstd"], target_spk),
        "14_hybrid_diag_affine_transform_plus_target_spk": (transformed["diag_affine"], target_spk),
        "15_hybrid_full_affine_transform_plus_target_spk": (transformed["full_affine"], target_spk),
    }
    for name in ridge_names:
        suffix = name.replace("ridge_full_affine_", "")
        conditions[f"ridge_pure_{suffix}_plus_source_spk"] = (transformed[name], source_spk)
        conditions[f"ridge_hybrid_{suffix}_plus_target_spk"] = (transformed[name], target_spk)
    for name in alpha_names:
        suffix = name.replace("alpha_", "")
        conditions[f"alpha_pure_{suffix}_plus_source_spk"] = (transformed[name], source_spk)
    outputs: dict[str, str] = {}
    for name, (features, embedding) in conditions.items():
        audio = model.synthesize(torchify(features, model.device), torchify(embedding[0], model.device))
        path = audio_dir / f"{name}.wav"
        sf.write(path, audio, 16000)
        outputs[name] = str(path)
    return outputs


def plot_trajectories(
    source: np.ndarray,
    target: np.ndarray,
    transformed: dict[str, np.ndarray],
    path: Path,
) -> None:
    shared = min(len(source), len(target))
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharex=True)
    for dim, ax in enumerate(axes.flat):
        ax.plot(source[:shared, dim], label="source", linewidth=1.2)
        ax.plot(target[:shared, dim], label="target", linewidth=1.2)
        ax.plot(transformed["meanstd"][:shared, dim], label="mean/std", linewidth=1.0)
        ax.plot(transformed["diag_affine"][:shared, dim], label="diag", linewidth=1.0)
        ax.plot(transformed["full_affine"][:shared, dim], label="full", linewidth=1.0)
        ax.set_title(ROI_NAMES[dim])
    axes.flat[0].legend(loc="best", fontsize=8)
    fig.suptitle("Aligned articulatory trajectories")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_meanstd(
    source_frames: np.ndarray,
    target_frames: np.ndarray,
    transformed: dict[str, np.ndarray],
    path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    x = np.arange(len(ROI_NAMES))
    width = 0.18
    series = {
        "source": source_frames,
        "target": target_frames,
        "mean/std": transformed["meanstd"],
        "diag": transformed["diag_affine"],
        "full": transformed["full_affine"],
    }
    for idx, (label, values) in enumerate(series.items()):
        axes[0].bar(x + idx * width, values.mean(axis=0), width, label=label)
        axes[1].bar(x + idx * width, values.std(axis=0), width, label=label)
    for ax, title in zip(axes, ["Mean", "Std"]):
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(ROI_NAMES)
        ax.set_title(title)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_full_affine(weight: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(weight, cmap="coolwarm", aspect="auto")
    ax.set_xticks(range(len(ROI_NAMES)))
    ax.set_yticks(range(len(ROI_NAMES)))
    ax.set_xticklabels(ROI_NAMES)
    ax.set_yticklabels(ROI_NAMES)
    ax.set_title("Full affine weight matrix")
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    manifest = args.manifest.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dirs = ensure_clean_dirs(output_dir)

    rows = read_manifest(manifest)
    if args.train_count < 1:
        raise ValueError("train-count must be >= 1")
    if len(rows) < args.train_count:
        raise ValueError("manifest does not contain enough rows for training")
    if args.test_index >= len(rows):
        raise ValueError("test-index is outside the manifest")

    os.chdir(ARTI6_ROOT)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    started = perf_counter()
    model = ARTI6(device=device)
    model.load_model()
    model_load_s = perf_counter() - started

    extracted = [extract_pair(model, row) for row in rows]
    train_pairs = extracted[: args.train_count]
    test_pair = extracted[args.test_index]
    average_spk = normalized_average_embedding(
        [
            embedding
            for pair in extracted
            for embedding in [pair["source_spk_emb"], pair["target_spk_emb"]]
            if isinstance(embedding, np.ndarray)
        ]
    )

    aligned_train = [aligned_frames(pair) for pair in train_pairs]
    train_source = np.concatenate([source for source, _ in aligned_train], axis=0)
    train_target = np.concatenate([target for _, target in aligned_train], axis=0)

    meanstd = fit_meanstd(train_source, train_target)
    diag_affine = fit_diag_affine(train_source, train_target)
    full_affine = fit_full_affine(train_source, train_target)
    ridge_affines = {
        f"ridge_full_affine_lam_{str(penalty).replace('.', 'p')}": fit_ridge_full_affine(
            train_source,
            train_target,
            penalty,
        )
        for penalty in args.ridge_lambdas
    }

    source_test = test_pair["source_arti"]
    target_test = test_pair["target_arti"]
    assert isinstance(source_test, np.ndarray)
    assert isinstance(target_test, np.ndarray)
    transformed = {
        "meanstd": transform_meanstd(source_test, meanstd),
        "diag_affine": transform_diag_affine(source_test, diag_affine),
        "full_affine": transform_full_affine(source_test, full_affine),
    }
    for name, params in ridge_affines.items():
        transformed[name] = transform_full_affine(source_test, params)

    alpha_names: list[str] = []
    for alpha in args.alphas:
        if alpha < 0 or alpha > 1:
            raise ValueError("alpha values must be between 0 and 1")
        alpha_tag = str(alpha).replace(".", "p")
        for base_name in ["diag_affine", "full_affine", *ridge_affines.keys()]:
            name = f"alpha_{base_name}_a_{alpha_tag}"
            transformed[name] = transform_residual_alpha(source_test, transformed[base_name], alpha)
            alpha_names.append(name)

    arrays = {
        "source_arti": source_test,
        "target_arti": target_test,
        "source_spk_emb": test_pair["source_spk_emb"],
        "target_spk_emb": test_pair["target_spk_emb"],
        "average_spk_emb": average_spk,
        **{f"transformed_{name}": value for name, value in transformed.items()},
    }
    for name, value in arrays.items():
        assert isinstance(value, np.ndarray)
        np.save(dirs["arrays"] / f"{name}.npy", value)
    np.save(dirs["arrays"] / "diag_affine_scale.npy", diag_affine["scale"])
    np.save(dirs["arrays"] / "diag_affine_bias.npy", diag_affine["bias"])
    np.save(dirs["arrays"] / "full_affine_weight.npy", full_affine["weight"])
    np.save(dirs["arrays"] / "full_affine_bias.npy", full_affine["bias"])
    for name, params in ridge_affines.items():
        np.save(dirs["arrays"] / f"{name}_weight.npy", params["weight"])
        np.save(dirs["arrays"] / f"{name}_bias.npy", params["bias"])

    audio_outputs = save_audio_conditions(
        model,
        test_pair,
        transformed,
        average_spk,
        list(ridge_affines.keys()),
        alpha_names,
        dirs["audio"],
    )
    plot_trajectories(source_test, target_test, transformed, dirs["plots"] / "trajectories.png")
    shared = min(len(source_test), len(target_test))
    plot_meanstd(
        source_test[:shared],
        target_test[:shared],
        {key: value[:shared] for key, value in transformed.items()},
        dirs["plots"] / "meanstd_comparison.png",
    )
    plot_full_affine(full_affine["weight"], dirs["plots"] / "full_affine_heatmap.png")

    summary = {
        "manifest": str(manifest),
        "device": device,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "model_load_s": round(model_load_s, 4),
        "train_count": args.train_count,
        "test_index": args.test_index,
        "train_utterance_ids": [pair["utterance_id"] for pair in train_pairs],
        "test_utterance_id": test_pair["utterance_id"],
        "train_frames": int(train_source.shape[0]),
        "alignment_policy": "truncate_each_train_pair_to_shared_min_length",
        "ridge_lambdas": args.ridge_lambdas,
        "alphas": args.alphas,
        "aligned_test_metrics": {
            "source_identity": regression_metrics(source_test, target_test),
            **{
                name: regression_metrics(value, target_test)
                for name, value in transformed.items()
            },
        },
        "tensor_summaries": {name: tensor_summary(value) for name, value in arrays.items()},
        "diag_affine": {
            "scale": diag_affine["scale"].tolist(),
            "bias": diag_affine["bias"].tolist(),
        },
        "full_affine": {
            "weight": full_affine["weight"].tolist(),
            "bias": full_affine["bias"].tolist(),
        },
        "ridge_full_affine": {
            name: {
                "lambda": float(params["lambda"]),
                "weight": params["weight"].tolist(),
                "bias": params["bias"].tolist(),
            }
            for name, params in ridge_affines.items()
        },
        "audio_outputs": audio_outputs,
        "plots": {
            "trajectories": str(dirs["plots"] / "trajectories.png"),
            "meanstd_comparison": str(dirs["plots"] / "meanstd_comparison.png"),
            "full_affine_heatmap": str(dirs["plots"] / "full_affine_heatmap.png"),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
