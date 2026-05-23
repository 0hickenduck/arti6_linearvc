# ARTI-6 + LinearVC Demo

## Current Stage

Before implementing LinearVC, first prove that the base ARTI-6 workflow works on the
lab GPU server with the smallest useful experiment.

## Minimal Validation Experiment

### Gate A — model-chain smoke test

Run ARTI-6 on the repository example wav:

```bash
.venv/bin/python arti6_linearvc_demo/run_arti6_smoke.py \
  --wav external/arti-6/example_gt.wav \
  --output-dir outputs/smoke/example
```

This validates:

- GPU visibility through PyTorch
- ARTI-6 checkpoint loading
- acoustic inversion
- articulatory synthesis
- output writing plus shape capture

### Gate B — dataset-chain smoke test

Prepare one same-prompt CMU ARCTIC pair (`bdl` → `slt`):

```bash
.venv/bin/python arti6_linearvc_demo/prepare_cmu_arctic_tiny.py \
  --root data/cmu_arctic \
  --source-speaker bdl \
  --target-speaker slt \
  --num-pairs 1 \
  --manifest data/manifests/cmu_arctic_tiny.csv
```

Then run ARTI-6 over the two wav files listed in the manifest. This validates the
dataset path before adding any LinearVC-specific logic.

## Why This Shape

Gate A tells us whether the base model works. Gate B tells us whether a real paired
dataset can enter the pipeline cleanly. Only after both pass should we add the first
LinearVC baseline and explicit articulatory transforms.

## First LinearVC Floor

Prepare six aligned CMU ARCTIC pairs:

```bash
.venv/bin/python arti6_linearvc_demo/prepare_cmu_arctic_tiny.py \
  --root data/cmu_arctic \
  --source-speaker bdl \
  --target-speaker slt \
  --num-pairs 6 \
  --manifest data/manifests/cmu_arctic_6pairs.csv
```

Then run:

```bash
# one-pair sanity floor
.venv/bin/python arti6_linearvc_demo/run_linearvc_floor.py \
  --manifest data/manifests/cmu_arctic_6pairs.csv \
  --output-dir outputs/linearvc_floor/sanity_1pair \
  --train-count 1 \
  --test-index 0

# five-pair train / one-pair test floor
.venv/bin/python arti6_linearvc_demo/run_linearvc_floor.py \
  --manifest data/manifests/cmu_arctic_6pairs.csv \
  --output-dir outputs/linearvc_floor/tiny_5train_1test \
  --train-count 5 \
  --test-index 5
```

The floor writes a condition matrix for isolating the role of articulatory transforms
versus speaker embedding injection:

1. source reconstruction
2. target reconstruction
3. embedding-only VC
4. oracle target articulation + source speaker embedding
5. source articulation + average speaker embedding
6. target articulation + average speaker embedding
7. pure mean/std articulatory transform + source speaker embedding
8. pure diagonal affine articulatory transform + source speaker embedding
9. pure full affine articulatory transform + source speaker embedding
10. average mean/std articulatory transform + average speaker embedding
11. average diagonal affine articulatory transform + average speaker embedding
12. average full affine articulatory transform + average speaker embedding
13. hybrid mean/std articulatory transform + target speaker embedding
14. hybrid diagonal affine articulatory transform + target speaker embedding
15. hybrid full affine articulatory transform + target speaker embedding

Conditions 7-9 are the strict Pure LinearVC test: the target voice must come from the
linear change in ARTI-6 features, not from swapping to the target speaker embedding.
Conditions 13-15 preserve the older hybrid setup for comparison.

Training alignment is intentionally primitive: each paired utterance is truncated to
its shared minimum length before frame-level fitting. That keeps the first run easy
to debug; better alignment can come after the pipeline proves itself.

## Scaling and Regularization Probe

After the tiny floor, prepare a larger paired manifest:

```bash
.venv/bin/python arti6_linearvc_demo/prepare_cmu_arctic_tiny.py \
  --root data/cmu_arctic \
  --source-speaker bdl \
  --target-speaker slt \
  --num-pairs 21 \
  --manifest data/manifests/cmu_arctic_21pairs.csv
```

Then run a 20-train / 1-test probe with ridge-regularized full affine maps and
partial residual transform strengths:

```bash
.venv/bin/python arti6_linearvc_demo/run_linearvc_floor.py \
  --manifest data/manifests/cmu_arctic_21pairs.csv \
  --output-dir outputs/linearvc_floor/scaling_20train_1test \
  --train-count 20 \
  --test-index 20 \
  --ridge-lambda 0.1 \
  --ridge-lambda 1.0 \
  --ridge-lambda 10.0 \
  --alpha 0.25 \
  --alpha 0.5
```

This probe asks whether more paired data, ridge regularization, or partial-strength
transforms can preserve intelligibility while moving the articulatory trajectory
toward the target. Treat lower trajectory MSE as a diagnostic only; voice-conversion
quality still needs listening because the current ARTI-6 decoder is explicitly
conditioned on speaker embeddings.

## Local Results Report

After running the floor, build a static report beside the experiment summary:

```bash
.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py \
  --summary outputs/linearvc_floor/tiny_5train_1test/summary.json
```

Open `outputs/linearvc_floor/tiny_5train_1test/index.html` on the same machine to
inspect the held-out metrics, listen to the six audio conditions, and view the
generated plots.

For remote viewing, build a portable zip bundle:

```bash
.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py \
  --summary outputs/linearvc_floor/tiny_5train_1test/summary.json \
  --bundle-zip
```

Download `outputs/linearvc_floor/tiny_5train_1test/tiny_5train_1test_report.zip`,
unzip it locally, then open the extracted `index.html`. The zip contains the report,
`summary.json`, all referenced audio files, and all referenced plots.

For the scaling probe, use:

```bash
.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py \
  --summary outputs/linearvc_floor/scaling_20train_1test/summary.json \
  --bundle-zip
```

Then download `outputs/linearvc_floor/scaling_20train_1test/scaling_20train_1test_report.zip`.

## Cross-Domain Timbre Shift Mapper Demo

The `05-22-cross-domain-timbre-shift` task pivots from ARTI-6 articulatory
linear transforms toward latent timbre steering. The first feasibility demo keeps
ARTI-6 as the frozen decoder, but shifts the ECAPA speaker embedding that ARTI-6
already extracts:

1. Route A fits a difference-of-means steering vector between paired source and
   target embeddings.
2. Route B trains a tiny residual MLP Micro-Mapper from source embeddings to
   target embeddings.
3. Both shifted embeddings are synthesized with the held-out source articulation
   so the output audio can be compared with source, target, and target-embedding
   oracle conditions.

Run the smallest held-out check from the existing 6-pair manifest:

```bash
.venv/bin/python arti6_linearvc_demo/run_timbre_shift_mapper.py \
  --manifest data/manifests/cmu_arctic_6pairs.csv \
  --output-dir outputs/timbre_shift_mapper/tiny_5train_1test \
  --train-count 5 \
  --test-index 5 \
  --epochs 400 \
  --bundle-zip
```

Download
`outputs/timbre_shift_mapper/tiny_5train_1test/tiny_5train_1test_report.zip`,
unzip it locally, then open `index.html` to inspect the embedding metrics, PCA
plot, Micro-Mapper loss curve, and comparative audio.

Important: this CMU ARCTIC run is an engineering smoke test only. The included
manifest is cross-speaker speaking data (`bdl` to `slt`), not same-speaker
cross-language or speech-to-singing data. The result proves the code path can
shift embeddings and synthesize audio; it should not be used as evidence for the
cross-domain timbre-shift claim. Use the same manifest schema once a true
cross-domain paired dataset is available.

### Same-Speaker Speech-to-Singing Dabble

Prepare a tiny GTSinger same-singer speech-to-singing manifest:

```bash
.venv/bin/python arti6_linearvc_demo/prepare_gtsinger_tiny.py \
  --root data/gtsinger_tiny \
  --manifest data/manifests/gtsinger_english_en_alto_1_6pairs.csv \
  --language English \
  --singer EN-Alto-1 \
  --num-pairs 6
```

Run the Route A / Route B demo:

```bash
.venv/bin/python arti6_linearvc_demo/run_timbre_shift_mapper.py \
  --manifest data/manifests/gtsinger_english_en_alto_1_6pairs.csv \
  --output-dir outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test \
  --train-count 5 \
  --test-index 5 \
  --epochs 400 \
  --bundle-zip
```

Build a blind listening-evaluation page and refresh the zip:

```bash
.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/summary.json \
  --bundle-zip
```

Download
`outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/gtsinger_en_alto_1_tiny_5train_1test_report.zip`,
unzip it locally, then open `index.html` for objective diagnostics and
`subjective_eval.html` for blind 1-5 listening ratings.

For a less adjacent same-singer validation split, spread rows across songs and
increase the training set:

```bash
.venv/bin/python arti6_linearvc_demo/prepare_gtsinger_tiny.py \
  --root data/gtsinger_tiny \
  --manifest data/manifests/gtsinger_english_en_alto_1_roundrobin_31pairs.csv \
  --language English \
  --singer EN-Alto-1 \
  --num-pairs 31 \
  --selection-strategy round-robin-songs

.venv/bin/python arti6_linearvc_demo/run_timbre_shift_mapper.py \
  --manifest data/manifests/gtsinger_english_en_alto_1_roundrobin_31pairs.csv \
  --output-dir outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep \
  --train-count 30 \
  --test-index 30 \
  --hidden-dim 128 \
  --epochs 1200 \
  --sweep-slider-alpha 0.25 \
  --sweep-slider-alpha 0.5 \
  --sweep-slider-alpha 0.75 \
  --sweep-slider-alpha 1.25 \
  --sweep-slider-alpha 1.5 \
  --synthesize-sweep-audio \
  --bundle-zip

.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep/summary.json \
  --bundle-zip
```

This round-robin validation is still not full singing conversion. It evaluates
whether a speech embedding can be steered toward the same speaker's singing-mode
timbre embedding. ARTI-6 remains a speech-oriented decoder, so the target
embedding oracle is the relevant upper bound for this demo.

The audio-sweep bundle contains the main comparison conditions plus Route A
wav files for `alpha=0.00`, `0.25`, `0.50`, `0.75`, `1.00`, `1.25`, and `1.50`:

```text
outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep_report.zip
```

Listening feedback on 2026-05-23 made this a negative result for the ARTI-6
audio path: the alpha sweep moves in embedding space but is not perceptually
salient, target reconstruction does not sound like real singing, and source
articulation plus target embedding remains close to the source speaking voice.
Use this bundle to document the failure mode; use a singing-aware decoder for
the next audible demo.

## Seed-VC Singing-Aware Pivot Demo

The first post-ARTI-6 pivot uses Seed-VC as a zero-shot singing voice conversion
decoder. This is not speech-to-singing yet: it uses a real singing source for
content and melody, then tests whether speech or singing reference audio can
condition the target singer timbre while preserving singing.

External model checkout:

```bash
git clone --depth 1 https://github.com/Plachtaa/seed-vc.git external/seed-vc
```

Install only the minimal Seed-VC inference dependencies into the project venv.
Do not install Seed-VC's full `requirements.txt` into this env because it pins an
older torch stack.

Run the GTSinger pivot demo:

```bash
.venv/bin/python arti6_linearvc_demo/run_seedvc_svc_demo.py \
  --root data/gtsinger_seedvc \
  --output-dir outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_30steps \
  --source-language English \
  --source-singer EN-Alto-1 \
  --source-song "yesterday once more" \
  --target-language English \
  --target-singer EN-Tenor-1 \
  --target-song Firework \
  --diffusion-steps 30 \
  --inference-cfg-rate 0.7 \
  --length-adjust 1.0 \
  --semi-tone-shift 0 \
  --bundle-zip

.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_30steps/summary.json \
  --reference-condition 03_target_singing_reference \
  --bundle-zip
```

Portable report:

```text
outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_30steps/gtsinger_en_alto1_to_en_tenor1_30steps_report.zip
```

The report contains source singing, target speech/singing references, source
speech reference, three converted singing outputs, an HTML listening page, a
blind subjective-eval page, Seed-VC logs, and speaker-similarity diagnostics.

First 30-step speaker-similarity probe:

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> target speech ref | 0.155 | 0.438 | 0.329 | 0.109 |
| source singing -> target singing ref | 0.017 | 0.358 | 0.545 | 0.071 |
| source singing -> source speech ref | 0.738 | 0.065 | 0.040 | 0.675 |

Second 30-step probe, EN-Tenor-1 -> EN-Alto-2:

```text
outputs/seedvc_pivot/gtsinger_en_tenor1_to_en_alto2_30steps/gtsinger_en_tenor1_to_en_alto2_30steps_report.zip
```

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> target speech ref | 0.142 | 0.468 | 0.453 | 0.013 |
| source singing -> target singing ref | 0.083 | 0.368 | 0.574 | -0.052 |
| source singing -> source speech ref | 0.567 | 0.106 | 0.062 | 0.720 |

This is the new audible-demo path to scale. The key next listening question is
whether `converted_target_speech_ref.wav` stays singing while moving toward the
target speaker using only a speech reference.

### Seed-VC English Triangle Matrix

Run a three-pair English matrix:

```bash
.venv/bin/python arti6_linearvc_demo/run_seedvc_svc_matrix.py \
  --root data/gtsinger_seedvc \
  --output-dir outputs/seedvc_pivot/english_triangle_30steps \
  --preset english-triangle \
  --diffusion-steps 30 \
  --inference-cfg-rate 0.7 \
  --length-adjust 1.0 \
  --semi-tone-shift 0 \
  --skip-existing \
  --bundle-zip
```

Portable report:

```text
outputs/seedvc_pivot/english_triangle_30steps/english_triangle_30steps_report.zip
```

The bundle contains an aggregate `index.html`, `matrix_summary.json`,
`matrix_metrics.csv`, and one full pair report plus blind eval page under each
`runs/<pair-id>/` directory.

30-step aggregate:

| Metric | Mean |
| --- | ---: |
| speech-prompt target advantage | 0.320 |
| singing-prompt target advantage | 0.439 |
| source-prompt source speech similarity | 0.741 |

### Seed-VC English -> Japanese Probe

Run one cross-language probe connected to the speech/singing × language idea:

```bash
.venv/bin/python arti6_linearvc_demo/run_seedvc_svc_demo.py \
  --root data/gtsinger_seedvc \
  --output-dir outputs/seedvc_pivot/gtsinger_en_alto1_to_ja_tenor1_30steps \
  --source-language English \
  --source-singer EN-Alto-1 \
  --source-song "yesterday once more" \
  --target-language Japanese \
  --target-singer JA-Tenor-1 \
  --target-song "Heartful Song" \
  --target-index 12 \
  --diffusion-steps 30 \
  --inference-cfg-rate 0.7 \
  --length-adjust 1.0 \
  --semi-tone-shift 0 \
  --bundle-zip

.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/seedvc_pivot/gtsinger_en_alto1_to_ja_tenor1_30steps/summary.json \
  --reference-condition 03_target_singing_reference \
  --bundle-zip
```

Portable report:

```text
outputs/seedvc_pivot/gtsinger_en_alto1_to_ja_tenor1_30steps/gtsinger_en_alto1_to_ja_tenor1_30steps_report.zip
```

Speaker-similarity probe:

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> Japanese speech ref | 0.208 | 0.317 | 0.444 | 0.127 |
| source singing -> Japanese singing ref | 0.175 | 0.269 | 0.608 | 0.154 |
| source singing -> source speech ref | 0.753 | 0.075 | 0.045 | 0.690 |

## Speaker-Domain Objective Evaluation

Use a speaker recognizer as an objective probe for the user-facing claim: a
same speaker should become harder to identify when enrollment and query cross the
speech/singing domain boundary.

```bash
.venv/bin/python arti6_linearvc_demo/run_speaker_domain_eval.py \
  --root data/gtsinger_domain_eval \
  --output-dir outputs/speaker_domain_eval/gtsinger_20spk_seed17_2enroll_2query \
  --num-speakers 20 \
  --enroll-per-domain 2 \
  --query-per-domain 2 \
  --selection-strategy seeded-random \
  --seed 17 \
  --bundle-zip
```

The script selects same-singer GTSinger speech/singing pairs, extracts
SpeechBrain ECAPA embeddings, and reports both:

- closed-set speaker-identification accuracy;
- speaker-verification EER from all enrolled-speaker centroid scores.

Portable report:

```text
outputs/speaker_domain_eval/gtsinger_20spk_seed17_2enroll_2query/gtsinger_20spk_seed17_2enroll_2query_report.zip
```

First 20-speaker run:

| Protocol | ID accuracy | EER | Same-speaker score | Impostor score |
| --- | ---: | ---: | ---: | ---: |
| speech enroll -> speech query | 0.950 | 0.024 | 0.722 | 0.176 |
| singing enroll -> singing query | 0.825 | 0.074 | 0.607 | 0.233 |
| speech enroll -> singing query | 0.700 | 0.125 | 0.390 | 0.124 |
| singing enroll -> speech query | 0.750 | 0.100 | 0.385 | 0.118 |

This objective eval is separate from synthesis quality. It validates that
speech/singing vocal-mode mismatch is visible to a modern speaker embedding
extractor, so it is a useful downstream metric for future timbre-shift models.

## Output Directory Format

The output tree is organized by experiment family and scale:

```text
outputs/
|-- linearvc_floor/
|   |-- sanity_1pair/
|   |-- tiny_5train_1test/
|   `-- scaling_20train_1test/
|-- speaker_domain_eval/
|   `-- gtsinger_20spk_seed17_2enroll_2query/
`-- timbre_shift_mapper/
    `-- gtsinger_en_alto_1_roundrobin_30train_1test_e1200/
```

`floor` means the lowest useful experimental baseline: a deliberately small run that
proves the pipeline can extract ARTI-6 features, fit simple linear transforms, synthesize
audio, and write diagnostics before we scale up. `sanity_1pair` is the bookkeeping/debug
run where one pair exercises the full path. `tiny_5train_1test` is the first held-out
floor: five same-prompt pairs fit the transform, and one pair is held out for metrics,
plots, and listening.
`scaling_20train_1test` uses twenty train pairs and one held-out pair, with extra ridge
and alpha conditions for checking whether regularization or partial transforms reduce
content damage.

Inside each run:

```text
audio/       wav conditions for listening
arrays/      saved numpy tensors and learned transform parameters
plots/       trajectory and transform diagnostics
summary.json machine-readable metadata, metrics, and artifact paths
index.html   generated local report
*_report.zip optional portable report bundle for local download
```

The report is intentionally scoped as a tiny floor check; it does not claim that the
method works beyond this small aligned split.
