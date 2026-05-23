# Project Brief: ARTI-6 + LinearVC

Status: PARTIAL GO

This project investigates interpretable articulatory voice conversion using ARTI-6 features and simple linear transformations.

## Target

ARTI-6 represents speech with six articulatory dimensions:

1. Lip Aperture (LA)
2. Tongue Tip (TT)
3. Tongue Body (TB)
4. Velum (VL)
5. Tongue Root (TR)
6. Larynx (LX)

## Research Question

Can speaker-dependent voice characteristics be represented as explicit transformations of low-dimensional articulatory trajectories?

## First Practical Demo

The first demo should answer:

Can we run ARTI-6 inversion and synthesis, then perform a simple source-to-target linear transformation on the 6D articulatory features, and synthesize converted speech?

## Eventual Pipeline

Step 1: ARTI-6 inversion

```text
source.wav -> source_arti_feats: (T, 6), source_spk_emb
target.wav -> target_arti_feats: (T, 6), target_spk_emb
```

Step 2: ARTI-6 reconstruction

```text
source_arti_feats + source_spk_emb -> source_reconstruction.wav
target_arti_feats + target_spk_emb -> target_reconstruction.wav
```

Step 3: embedding-only VC baseline

```text
source_arti_feats + target_spk_emb -> vc_embedding_only.wav
```

Step 4: articulatory linear transform

```text
transformed_source_arti = W source_arti + b
```

Then synthesize:

```text
transformed_source_arti + source_spk_emb -> vc_arti_transform_only.wav
transformed_source_arti + target_spk_emb -> vc_arti_transform_plus_target_spk.wav
```

## Most Important Comparison

```text
source_arti_feats + target_spk_emb
vs.
transformed_source_arti + target_spk_emb
```

This tests whether articulatory transformation contributes beyond the target speaker embedding.

## Current Constraints

- We are not on the lab server.
- ARTI-6 has not been run.
- ARTI-6 API has not been verified.
- Checkpoint availability has not been verified by execution.
- Dataset local path is unknown.
- CUDA/PyTorch environment is unknown.
- No datasets or model checkpoints should be downloaded in this phase.
