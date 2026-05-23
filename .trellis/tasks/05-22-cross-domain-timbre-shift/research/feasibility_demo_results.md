# Cross-Domain Timbre Shift Feasibility Demo Results

**Date:** 2026-05-22  
**Demo command:**

```bash
.venv/bin/python arti6_linearvc_demo/run_timbre_shift_mapper.py \
  --manifest data/manifests/cmu_arctic_6pairs.csv \
  --output-dir outputs/timbre_shift_mapper/tiny_5train_1test \
  --train-count 5 \
  --test-index 5 \
  --epochs 400 \
  --bundle-zip
```

## What Was Implemented

- Route A: difference-of-means latent steering vector over ARTI-6 ECAPA speaker embeddings.
- Route B: residual MLP Micro-Mapper trained from source embeddings to target embeddings.
- Frozen decoder path: shifted embeddings are passed into ARTI-6 synthesis with held-out source articulation.
- Output report: `outputs/timbre_shift_mapper/tiny_5train_1test/index.html`.
- Portable bundle: `outputs/timbre_shift_mapper/tiny_5train_1test/tiny_5train_1test_report.zip`.

## Held-Out Result

The held-out row is `a0006`, trained on `a0001` through `a0005`.

| Condition | Cosine to target embedding | MSE to target embedding |
| --- | ---: | ---: |
| Unshifted source embedding | -0.0311 | 0.0107 |
| Route A slider | 0.6212 | 0.0039 |
| Route B Micro-Mapper | 0.7416 | 0.0027 |
| Target embedding oracle | 1.0000 | 0.0000 |

Both routes moved the source embedding toward the held-out target. Route B was the
best method in this run, with a cosine gain of `0.7728` over the unshifted source.

## Feasibility Read

This direction is technically feasible in the current repo because ARTI-6 already
provides:

- an ECAPA-TDNN speaker embedding extractor,
- a frozen synthesizer conditioned by the speaker embedding,
- a working paired-manifest and report-output pattern.

The main research limitation remains dataset validity. The current CMU ARCTIC
manifest is cross-speaker speaking data (`bdl` to `slt`), not same-speaker
cross-language or speaking-to-singing data. This run should be treated as an
engineering smoke test only. It proves the machinery can steer and synthesize
embeddings, but it does not yet prove the thesis claim about cross-domain timbre
drift.

## Next Practical Direction

Use the same manifest schema with a true paired cross-domain dataset:

- same speaker, speech and singing,
- or same speaker, L1 and L2/cross-language recordings,
- with enough pairs to hold out speakers or utterances.

Then compare Route A and Route B against unshifted and target-embedding oracle
audio, using both embedding metrics and listening tests.

Candidate datasets and the automatic dataset-discovery track are recorded in
`research/cross_domain_dataset_candidates.md`.
