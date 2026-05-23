# Experiment Design

Status: PARTIAL GO

## Minimal Demo

Goal: show whether a simple source-to-target transform in six-dimensional ARTI-6 space changes converted speech beyond a target-speaker embedding baseline.

The critical ablation is:

```text
source_arti_feats + target_spk_emb
vs.
transformed_source_arti + target_spk_emb
```

## Dataset

Dataset preference: CMU ARCTIC.

Preferred speakers:

- source speaker: bdl
- target speaker: slt

Status: UNKNOWN until verified. Do not assume the dataset exists locally, that these speaker folders exist, or that prompt IDs are paired until inspected from real paths.

## Training And Testing Split

Training:

- 5 to 20 paired utterances.

Testing:

- 1 to 3 paired utterances.

Pairing should initially prefer same-prompt utterances if CMU ARCTIC layout confirms shared prompt IDs across bdl and slt.

## Transform Methods

1. Mean/std transform, no alignment required.

   For each articulatory dimension, map source statistics to target statistics:

   ```text
   a'_d = ((a_d - mean_source_d) / std_source_d) * std_target_d + mean_target_d
   ```

   This is the safest first transform because it does not require frame alignment.

2. Diagonal affine transform, length normalization required.

   Fit per-dimension affine parameters:

   ```text
   a'_d = w_d * a_d + b_d
   ```

   Requires source and target trajectories to have matched frame lengths. Initial length normalization can use simple resampling per utterance, but this may create artifacts.

3. Full affine / ridge regression, length normalization required.

   Fit:

   ```text
   a' = W a + b
   ```

   Use ridge regularization because training may only contain 5 to 20 utterances.

## Later Design Note: GMM Transform

Do not implement GMM yet.

Potential later form:

```text
F(a) = sum_k p(k|a)(W_k a + b_k), K = 2 or 4
```

This is deferred until the basic mean/std, diagonal affine, and full affine comparisons are understood.

## Required Ablation Audio Later

- `01_source_original.wav`
- `02_target_reference.wav`
- `03_source_reconstruction.wav`
- `04_target_reconstruction.wav`
- `05_embedding_only_vc.wav`
- `06_meanstd_transform_only_source_spk.wav`
- `07_meanstd_transform_plus_target_spk.wav`
- `08_diag_affine_transform_plus_target_spk.wav`
- `09_full_affine_transform_plus_target_spk.wav`

## Required Saved Arrays Later

- `source_arti.npy`
- `target_arti.npy`
- `transformed_arti.npy`
- `source_spk_emb.npy`
- `target_spk_emb.npy`

## Required Diagnostics

- Plot source ARTI-6 trajectories.
- Plot transformed ARTI-6 trajectories.
- Plot target ARTI-6 trajectories.
- Plot per-dimension mean/std before and after transform.
- Plot full affine `W` heatmap.
- Print shape and range of every tensor.

## Initial Success Criteria

- ARTI-6 inversion produces `(T, 6)` features for source and target wavs.
- Reconstruction audio can be synthesized from extracted ARTI-6 features and original speaker embeddings.
- Embedding-only VC audio can be synthesized.
- At least mean/std transformed features can be synthesized with target speaker embedding.
- The comparison between embedding-only and transform-plus-target-speaker is available as audio and diagnostics.
