# GTSinger Speech-to-Singing Dabble Experiment

**Date:** 2026-05-22  
**Goal:** Move beyond the CMU ARCTIC engineering smoke test and run a real
same-speaker cross-domain demo using speech-to-singing pairs.

## Dataset

Dataset: GTSinger (`AaronZ345/GTSinger` on Hugging Face)  
License on dataset card: `cc-by-nc-sa-4.0`  
Subset used: `English`, singer `EN-Alto-1`, 6 paired speech/singing rows.

The GTSinger metadata has one row per singing segment and includes both:

- `speech_fn`: same singer's paired speech recording,
- `wav_fn`: same singer's singing recording.

This matches the project manifest contract for `source_domain=speech` and
`target_domain=singing`.

## Data Prep Command

```bash
.venv/bin/python arti6_linearvc_demo/prepare_gtsinger_tiny.py \
  --root data/gtsinger_tiny \
  --manifest data/manifests/gtsinger_english_en_alto_1_6pairs.csv \
  --language English \
  --singer EN-Alto-1 \
  --num-pairs 6
```

Output manifest:

```text
data/manifests/gtsinger_english_en_alto_1_6pairs.csv
```

## Demo Command

```bash
.venv/bin/python arti6_linearvc_demo/run_timbre_shift_mapper.py \
  --manifest data/manifests/gtsinger_english_en_alto_1_6pairs.csv \
  --output-dir outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test \
  --train-count 5 \
  --test-index 5 \
  --epochs 400 \
  --bundle-zip
```

## Subjective Evaluation Page

```bash
.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/summary.json \
  --bundle-zip
```

The page uses the target reconstruction as a reference and asks for 1-5 ratings
on:

- Naturalness
- Singing-likeness / target-domain match
- Timbre similarity to target reference

Output files:

- `outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/index.html`
- `outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/subjective_eval.html`
- `outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/subjective_eval_key.json`
- `outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/gtsinger_en_alto_1_tiny_5train_1test_report.zip`

## Objective Embedding Metrics

Held-out item: `English__EN-Alto-1__Breathy__all is found__Breathy_Group__0005`

| Condition | Cosine to target singing embedding | MSE to target singing embedding |
| --- | ---: | ---: |
| Source speech embedding | 0.4469 | 0.0058 |
| Route A difference-of-means slider | 0.6646 | 0.0035 |
| Route B Micro-Mapper | 0.7166 | 0.0030 |
| Target singing oracle | 1.0000 | 0.0000 |

Both Route A and Route B move the same-speaker speech embedding toward the same
speaker's singing embedding. Route B is best on this held-out dabble.

## Evaluation Design

### Objective Checks

Use objective checks as sanity diagnostics only:

- ECAPA cosine/MSE to held-out target-domain embedding.
- Route A / Route B improvement over unshifted source embedding.
- Training loss convergence.
- Artifact validity: every referenced audio/plot exists and the zip contains
  report, audio, plots, arrays, model state, and subjective evaluation files.

These metrics cannot prove perceptual quality because the embedding extractor is
also part of the manipulated representation.

### Subjective Checks

The first meaningful evaluation should be a small blind listening test:

- Conditions: source reconstruction, target-embedding oracle, Route A, Route B.
- Reference: target singing reconstruction.
- Rating dimensions: naturalness, singing-likeness, timbre similarity to target.
- Minimum dabble: the user rates one held-out item.
- Next scale-up: 5-10 held-out utterances and 3+ raters.

## Current Interpretation

This is now a valid same-speaker cross-domain demo, unlike the CMU ARCTIC smoke
test. The scope is still tiny: one singer, one song, five train pairs and one
held-out pair. It is enough to justify continuing, but not enough to claim a
general method.

Next useful experiments:

1. Run the same setup across multiple GTSinger singers and languages.
2. Hold out songs, not just neighboring segments.
3. Add WavLM or another embedding extractor to avoid overfitting conclusions to
   ECAPA alone.
4. Collect subjective ratings and compare Route A vs Route B vs oracle.
