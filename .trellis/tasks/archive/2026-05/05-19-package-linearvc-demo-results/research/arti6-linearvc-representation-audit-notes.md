# ARTI-6 LinearVC representation audit notes

Date: 2026-05-20

## Context

The initial idea was to test whether ARTI-6's 6D articulatory representation could serve as the LinearVC transform space: learn a linear source-to-target map over articulatory trajectories, synthesize with a fixed source speaker embedding, and obtain target-like timbre from the transformed representation.

## Experiments run

### Tiny floor: 5 train / 1 held-out

Output:

- `outputs/linearvc_floor/tiny_5train_1test/`
- `outputs/linearvc_floor/tiny_5train_1test/tiny_5train_1test_report.zip`

Conditions added:

- source reconstruction
- target reconstruction
- embedding-only VC
- oracle target articulation + source speaker embedding
- average speaker embedding controls
- pure mean/std, diagonal affine, and full affine transforms with source speaker embedding
- hybrid transforms with target speaker embedding

Observation from listening:

- Source and target reconstructions are good.
- Embedding-only VC is strong.
- Mean/std transform sounds close to embedding-only or source-conditioned baselines.
- Diagonal/full affine transforms mostly damage intelligibility/content; apparent timbre change comes mainly from target speaker embedding in hybrid conditions.

### Scaling probe: 20 train / 1 held-out

Output:

- `outputs/linearvc_floor/scaling_20train_1test/`
- `outputs/linearvc_floor/scaling_20train_1test/scaling_20train_1test_report.zip`

Added:

- ridge-regularized full affine maps with lambdas `0.1`, `1.0`, `10.0`
- partial residual alpha variants with alpha `0.25`, `0.5`

Numerical trajectory metrics improved relative to source identity, but this did not imply audible voice conversion. The working interpretation remains that trajectory MSE is not sufficient for VC quality in this representation.

## Current interpretation

The current pretrained ARTI-6 synthesis model is explicitly conditioned as:

```text
audio = synthesis(arti6_6d_features, speaker_embedding)
```

The 6D features appear to act primarily as a phonetic/articulatory content bottleneck. Speaker individuality/timbre is largely controlled by the ECAPA speaker embedding. Under this design, failure of pure 6D LinearVC is not necessarily a model defect; it may indicate that ARTI-6 is doing the intended separation between articulatory content and speaker identity.

## Research pivot

The stronger paper direction is not "make ARTI-6 pure LinearVC work at all costs." A better question is:

```text
Why does LinearVC work in high-dimensional SSL acoustic feature spaces, but not in ARTI-6's low-dimensional articulatory bottleneck?
```

Candidate next steps:

1. Speaker predictability audit:
   - train small classifiers from ARTI-6 feature summaries vs WavLM feature summaries to speaker ID.
   - expected: WavLM retains more speaker information than ARTI-6.
2. Same-prompt content audit:
   - compare same-prompt cross-speaker distances vs different-prompt distances in ARTI-6 and WavLM spaces.
   - expected: ARTI-6 clusters more by utterance/content than by speaker.
3. LinearVC contrast:
   - compare ARTI-6 6D affine transforms against WavLM-layer linear transforms on the same source/target split.
   - use listening plus speaker-sim/content diagnostics; do not rely on trajectory MSE alone.

## Practical conclusion

Do not spend more time adding tricks to direct ARTI-6 6D affine transforms unless a diagnostic specifically requires it. Prefer lightweight representation audits and SSL LinearVC contrast experiments before considering any new large decoder training.
