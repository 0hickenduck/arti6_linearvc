# Objective Clarification and Round-Robin Validation

**Date:** 2026-05-22  
**Updated:** 2026-05-23  
**Reason:** Listening feedback showed that ARTI-6 target reconstruction does not
preserve a convincing singing melody. A later audio-sweep listen showed that the
target-embedding oracle and alpha slider also fail to create a perceptually
salient timbre change.

## Clarified Research Target

The current ARTI-6-based demo should not claim full speech-to-singing conversion.
The decoder is not a singing decoder, and the articulatory stream does not carry a
usable melody/F0 singing contour through this pipeline.

The initially defensible target was narrower:

> Predict or steer the same speaker's **singing vocal-mode timbre embedding** from
> their speech embedding, then apply that embedding to a frozen decoder as a
> controllable timbre/style condition.

This means:

- Route A is a vocal-mode slider: `speech_embedding + alpha * mean(singing - speech)`.
- Route B is a mapper from speech embedding to singing-mode embedding.
- Target-embedding oracle was treated as the upper bound for the
  embedding-conditioned timbre.
- Listening tests should ask whether the output has more singing-like vocal
  quality / target timbre, not whether it sings the song.

The 2026-05-23 listening result weakens this ARTI-6 framing. Even if the
embedding-space metric improves, ARTI-6 does not make the embedding shift audible
enough to function as a demo. This should now be treated as a negative result for
the ARTI-6 synthesis path, not as a training-scale issue.

## More Robust GTSinger Split

The first GTSinger run used adjacent segments from one song. I added a
round-robin song selection strategy so the manifest spans many songs and singing
techniques for the same singer.

Data prep:

```bash
.venv/bin/python arti6_linearvc_demo/prepare_gtsinger_tiny.py \
  --root data/gtsinger_tiny \
  --manifest data/manifests/gtsinger_english_en_alto_1_roundrobin_31pairs.csv \
  --language English \
  --singer EN-Alto-1 \
  --num-pairs 31 \
  --selection-strategy round-robin-songs
```

Demo run:

```bash
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
```

Subjective evaluation page:

```bash
.venv/bin/python arti6_linearvc_demo/build_subjective_eval.py \
  --summary outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep/summary.json \
  --bundle-zip
```

Portable report:

```text
outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_report.zip
```

Audio-sweep report:

```text
outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep_report.zip
```

The audio-sweep run includes the five main comparison wav files plus Route A wav
files at `alpha=0.00`, `0.25`, `0.50`, `0.75`, `1.00`, `1.25`, and `1.50`.
It also includes `subjective_eval.html` and `subjective_eval_key.json` after
running `build_subjective_eval.py` against the audio-sweep summary.

## Held-Out Embedding Result

Held-out item:
`English__EN-Alto-1__Mixed_Voice_and_Falsetto__yesterday once more__Control_Group__0000`

| Condition | Cosine to target singing embedding | MSE |
| --- | ---: | ---: |
| Source speech embedding | 0.6516 | 0.0036 |
| Route A slider (`alpha=1.0`) | 0.7364 | 0.0027 |
| Route B Micro-Mapper | 0.6966 | 0.0032 |
| Target singing oracle | 1.0000 | 0.0000 |

## Route A Alpha Sweep

| Alpha | Cosine | MSE |
| ---: | ---: | ---: |
| 0.00 | 0.6516 | 0.0036 |
| 0.25 | 0.6880 | 0.0032 |
| 0.50 | 0.7157 | 0.0030 |
| 0.75 | 0.7322 | 0.0028 |
| 1.00 | 0.7364 | 0.0027 |
| 1.25 | 0.7291 | 0.0028 |
| 1.50 | 0.7123 | 0.0030 |

## Interpretation

The larger same-singer split changes the story:

- More training data does help the statistical slider.
- The best alpha is around `1.0`; over-steering past `1.25` begins to hurt.
- Route B still improves over the unshifted source, but underperforms Route A in
  this split. With only one singer, the MLP may be overfitting local variation
  instead of learning a better global singing-mode transform.

The audio-sweep listening changes the story again:

- The slider movement is objectively measurable in embedding space, but not
  perceptually salient in the rendered audio.
- Target reconstruction does not sound like singing; it sounds like stretched
  speech-like vocalization.
- Source articulation plus target embedding remains close to the source speaking
  voice, so the target embedding is not an audible upper bound in this decoder.
- The bottleneck is the frozen ARTI-6 acoustic/articulatory synthesis path, not
  merely insufficient Micro-Mapper training.

Current best framing:

1. Keep Route A as an embedding-space baseline and diagnostic.
2. Treat Route B as a candidate nonlinear refinement only after moving to
   multi-singer data and a decoder where the embedding affects audible timbre.
3. Do not use ARTI-6 audio as the final speech-to-singing or timbre-shift demo.
4. Move audible demos to a singing-aware decoder/prosody path that can model F0,
   duration, breath, phonation, and musical prosody.

The audio-sweep output is the right artifact for the immediate listening
question: whether the embedding slider creates an audible timbre change. It is
not the final demo because every alpha still uses the same source articulation
and the same speech-oriented ARTI-6 decoder.

Listening answered that question negatively for this path: the slider does not
produce a reliable audible change despite the objective embedding movement.

## Next Experiment

Run a multi-singer validation:

- Train Route A as a global speech-to-singing delta across many singers.
- Train Route B with leave-one-singer-out or leave-one-song-out splits.
- Report both embedding metrics and blind listening ratings.
- Replace or augment the decoder with a singing-capable acoustic/singing voice
  conversion model before spending more effort on perceptual audio demos.
