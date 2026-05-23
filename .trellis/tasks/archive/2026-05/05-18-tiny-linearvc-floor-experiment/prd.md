# tiny-linearvc-floor-experiment

## Goal

Build and run the first minimal ARTI-6 + LinearVC floor experiment on `valkyrie08`: use 6D articulatory features as the transformed representation, prove the pipeline on one aligned pair, then fit and evaluate tiny linear maps on a very small paired CMU ARCTIC split before scaling up.

## What I already know

* Base ARTI-6 inference and synthesis already run successfully on GPU on `valkyrie08`.
* A tiny CMU ARCTIC paired manifest (`bdl`→`slt`) already works for one same-prompt pair.
* The research question is whether explicit linear transforms over 6D articulatory trajectories contribute beyond changing only the target speaker embedding.
* The floor experiment should optimize for debuggability before scientific breadth.

## Assumptions

* The first floor should transform ARTI-6 articulatory features, not acoustic features.
* Same-prompt paired utterances allow simple frame alignment experiments before introducing a more complex temporal model.
* We should prefer tiny, inspectable outputs over a larger run until all plots and invariants look sane.

## Requirements

1. Implement a reproducible tiny LinearVC pipeline under `arti6_linearvc_demo/`.
2. Use a two-stage experiment design:
   - Stage 1: one-pair sanity floor
   - Stage 2: five-pair train / one-pair test tiny floor
3. Produce these conditions for at least the test pair:
   - source reconstruction
   - target reconstruction
   - embedding-only VC baseline
   - mean/std transformed VC
   - diagonal affine transformed VC
   - full affine transformed VC
4. Save tensor artifacts, plots, audio outputs, manifests, and a machine-readable summary.
5. Add explicit diagnostics for shape, min/max, NaN/Inf, and learned transform parameters so bugs surface quickly.

## Acceptance Criteria

* [x] One-pair sanity floor runs end-to-end without manual intervention.
* [x] 5-train / 1-test tiny experiment runs end-to-end on GPU.
* [x] All six output conditions are written for the test utterance.
* [x] Articulatory feature arrays, speaker embeddings, plots, and transform matrices are saved.
* [x] Summary JSON records shapes, ranges, fit settings, and output paths.
* [x] Results are organized so the next experiment can scale from the same code path.

## Out of Scope

* Full-dataset training.
* Perceptual evaluation / MOS.
* Sophisticated temporal alignment beyond the smallest viable baseline needed for same-prompt pairs.
* Any claim that the method works scientifically before the tiny floor is inspected.

## Experiment Design

### Stage 1 — one-pair sanity floor

Use one same-prompt `bdl`→`slt` pair.

Outputs:
1. source reconstruction = `source_arti + source_spk_emb`
2. target reconstruction = `target_arti + target_spk_emb`
3. embedding-only VC = `source_arti + target_spk_emb`
4. mean/std transform VC = `meanstd(source_arti -> target_arti) + target_spk_emb`

Purpose: confirm the full data/model/output path and catch bookkeeping or synthesis bugs immediately.

### Stage 2 — tiny fitted floor

Use five aligned pairs for train, one held-out pair for test.

Maps:
1. per-dimension mean/std transform
2. diagonal affine transform
3. full affine 6x6 transform

Diagnostics:
* source/target/transformed trajectory plots
* per-dimension mean/std before and after
* learned diagonal parameters
* learned full affine matrix heatmap
* shape/range/NaN checks for every saved tensor

## Completion Bar

If both stages run cleanly and outputs are interpretable, we can move to the actual first research comparison without needing the user to steer implementation details.

## Results

* One-pair sanity floor completed on CUDA and wrote six audio conditions plus plots/arrays.
* Tiny floor completed with five train pairs (`a0001`–`a0005`) and held-out test `a0006`.
* Held-out aligned-frame metrics on `a0006`:
  * source identity: MSE `0.23069`, MAE `0.31186`
  * mean/std: MSE `0.22125`, MAE `0.30350`
  * diagonal affine: MSE `0.16811`, MAE `0.27560`
  * full affine: MSE `0.15701`, MAE `0.27054`
* Full affine gives the best first-floor numerical fit, but plots show smoothing and the current alignment is deliberately crude; this is evidence to continue, not evidence to overclaim.
