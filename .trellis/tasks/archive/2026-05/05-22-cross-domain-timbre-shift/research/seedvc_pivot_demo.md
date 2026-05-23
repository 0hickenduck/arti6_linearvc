# Seed-VC Singing-Aware Pivot Demo

**Date:** 2026-05-23  
**Reason:** ARTI-6 produced an embedding-space movement but failed as an audible
singing/timbre demo. We need a decoder that can actually render singing.

## Model Choice

Seed-VC is a practical first pivot because it supports zero-shot singing voice
conversion and F0 conditioning. It can use a singing source for content and
melody, then use speech or singing reference audio as the target voice prompt.

Sources:

- GitHub: https://github.com/Plachtaa/seed-vc
- Paper: https://arxiv.org/abs/2411.09943

Important scope clarification: this first pivot is **singing voice conversion**,
not speech-to-singing generation. It answers the immediate decoder question:
can the harness produce singing audio whose timbre is controlled by speech or
singing references? A later model can attempt speech-to-singing directly.

## Environment

External checkout:

```text
external/seed-vc
```

Do not install Seed-VC's full `requirements.txt` into the project venv because it
pins an older torch stack. The project venv kept:

- Python 3.9.2
- Torch `2.8.0+cu128`
- CUDA on NVIDIA RTX 6000 Ada Generation

Minimal extra dependencies installed for inference included `munch`, `einops`,
and `descript-audio-codec`.

## Smoke Test

Command:

```bash
cd external/seed-vc
PYTHONPATH=. ../../.venv/bin/python inference.py \
  --source "examples/source/TECHNOPOLIS - 2085 [vocals]_[cut_14sec].wav" \
  --target examples/reference/s1p1.wav \
  --output ../../outputs/seedvc_pivot/smoke_example \
  --diffusion-steps 4 \
  --length-adjust 1.0 \
  --inference-cfg-rate 0.7 \
  --f0-condition True \
  --auto-f0-adjust False \
  --fp16 True
```

Result:

```text
outputs/seedvc_pivot/smoke_example/vc_TECHNOPOLIS - 2085 [vocals]_[cut_14sec]_s1p1_1.0_4_0.7.wav
```

This confirmed that the Seed-VC checkpoint path, Whisper content encoder,
RMVPE/F0 path, BigVGAN vocoder, CUDA runtime, and output writing all work on the
server.

## Implemented Harness

Script:

```text
arti6_linearvc_demo/run_seedvc_svc_demo.py
```

It:

1. Selects source and target GTSinger rows.
2. Downloads the exact speech and singing files.
3. Copies source singing, source speech reference, target speech reference, and
   target singing reference into `audio/`.
4. Runs Seed-VC with `--f0-condition True`.
5. Produces three converted outputs:
   - source singing -> target speech reference;
   - source singing -> target singing reference;
   - source singing -> source speech reference.
6. Extracts speaker embeddings with `speechbrain/spkrec-ecapa-voxceleb`.
7. Reports converted-output similarity to source singing, target speech, target
   singing, and source speech references.
8. Writes `summary.json`, `index.html`, logs, selection manifest, and zip.

## Main 30-Step Run

Command:

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
```

Subjective evaluation page:

```bash
.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_30steps/summary.json \
  --reference-condition 03_target_singing_reference \
  --bundle-zip
```

Portable report:

```text
outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_30steps/gtsinger_en_alto1_to_en_tenor1_30steps_report.zip
```

Selected items:

- Source singing: `English#EN-Alto-1#Mixed_Voice_and_Falsetto#yesterday once more#Control_Group#0000`
- Target reference: `English#EN-Tenor-1#Mixed_Voice_and_Falsetto#Firework#Control_Group#0000`

Run metadata:

- Diffusion steps: 30
- F0 conditioning: true
- Auto F0 adjust: false
- Inference CFG rate: 0.7
- Conversion elapsed times: about 9.7-10.0 seconds each
- Total harness elapsed time: 32.94 seconds

## 30-Step Speaker-Similarity Probe

### EN-Alto-1 -> EN-Tenor-1

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> target speech ref | 0.155 | 0.438 | 0.329 | 0.109 |
| source singing -> target singing ref | 0.017 | 0.358 | 0.545 | 0.071 |
| source singing -> source speech ref | 0.738 | 0.065 | 0.040 | 0.675 |

### EN-Tenor-1 -> EN-Alto-2

Command used the same settings with source singer `EN-Tenor-1`, source song
`Firework`, target singer `EN-Alto-2`, and target song `Call Me Maybe`.

Portable report:

```text
outputs/seedvc_pivot/gtsinger_en_tenor1_to_en_alto2_30steps/gtsinger_en_tenor1_to_en_alto2_30steps_report.zip
```

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> target speech ref | 0.142 | 0.468 | 0.453 | 0.013 |
| source singing -> target singing ref | 0.083 | 0.368 | 0.574 | -0.052 |
| source singing -> source speech ref | 0.567 | 0.106 | 0.062 | 0.720 |

This objective probe is directionally sane:

- When prompted by target speech, the converted output is closest to target
  speech.
- When prompted by target singing, the converted output is closest to target
  singing.
- When prompted by source speech, the converted output stays close to source
  identity.

This is much stronger than the ARTI-6 audio path because the output is generated
by a singing-aware model with F0 conditioning rather than a speech-oriented
articulatory decoder.

## English Triangle Matrix

Script:

```text
arti6_linearvc_demo/run_seedvc_svc_matrix.py
```

Command:

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

The aggregate report contains three singer-pair runs, each with source singing,
target speech/singing references, source speech reference, three converted
outputs, a pair-level report, and a blind listening page.

Aggregate stats:

| Metric | Mean |
| --- | ---: |
| speech prompt -> target speech | 0.558 |
| speech prompt -> target singing | 0.423 |
| speech-prompt target advantage | 0.320 |
| singing prompt -> target singing | 0.596 |
| singing-prompt target advantage | 0.439 |
| source prompt -> source speech | 0.741 |

Per-pair target advantages:

| Pair | Speech-prompt target advantage | Singing-prompt target advantage | Source-prompt source speech |
| --- | ---: | ---: | ---: |
| EN-Alto-1 -> EN-Tenor-1 | 0.306 | 0.421 | 0.687 |
| EN-Tenor-1 -> EN-Alto-2 | 0.339 | 0.486 | 0.706 |
| EN-Alto-2 -> EN-Alto-1 | 0.314 | 0.409 | 0.830 |

Interpretation: the direction is stable across the three English pairs. Speech
references move the output toward target identity, but singing references remain
stronger. This matches listening feedback that the reference works but is not as
strong as we ultimately want.

## English -> Japanese Cross-Language Probe

This probe connects the Seed-VC pivot to the new speech/singing × language
question. It is **not** a strict same-person multilingual demo; it is a
cross-singer, cross-language SVC probe.

Command:

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

Selected items:

- Source: `English#EN-Alto-1#Mixed_Voice_and_Falsetto#yesterday once more#Control_Group#0000`
- Target: `Japanese#JA-Tenor-1#Breathy#Heartful Song#Control_Group#0000`

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> target speech ref | 0.208 | 0.317 | 0.444 | 0.127 |
| source singing -> target singing ref | 0.175 | 0.269 | 0.608 | 0.154 |
| source singing -> source speech ref | 0.753 | 0.075 | 0.045 | 0.690 |

The Japanese speech prompt does move away from source identity and toward target
identity, but the Japanese singing prompt remains much stronger. This gives a
concrete listening demo for the language/reference-mode hypothesis.

## Earlier 8-Step Smoke Run

The 8-step run validated the same harness quickly:

```text
outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_8steps/gtsinger_en_alto1_to_en_tenor1_8steps_report.zip
```

The 30-step run should be used for listening unless speed is the priority.

## Next Scale-Up

1. Listen to the 30-step bundle first and check whether the output is clearly
   singing and whether target speech reference moves the timbre.
2. Listen to the English triangle and English->Japanese bundles.
3. Add a matched condition where target speech and target singing references are
   from the same target row, then compare whether speech references are
   sufficient to control singing timbre.
4. Add stronger objective evaluation: speaker verification EER across converted
   outputs, not only pairwise cosine to four references.
5. Search for or mine strict same-person multilingual speech/singing data.
6. If target-speech prompting works, train or adapt a mapper that predicts the
   best singing-reference conditioning from speech references.
