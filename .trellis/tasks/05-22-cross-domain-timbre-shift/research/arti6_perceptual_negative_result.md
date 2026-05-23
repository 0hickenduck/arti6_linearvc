# ARTI-6 Perceptual Negative Result

**Date:** 2026-05-23  
**Source:** User listening feedback on the GTSinger round-robin audio-sweep demo.

## Context

The ARTI-6 sandbox was used to test whether a speech embedding can be shifted
toward a same-speaker singing embedding and then rendered by a frozen
articulatory synthesizer. The objective embedding metrics moved in the expected
direction:

| Condition | Cosine to target singing embedding |
| --- | ---: |
| Source speech embedding | 0.6516 |
| Route A slider (`alpha=1.0`) | 0.7364 |
| Route B Micro-Mapper | 0.6966 |
| Target singing oracle | 1.0000 |

The audio-sweep bundle contains Route A alpha wav files at `0.00`, `0.25`,
`0.50`, `0.75`, `1.00`, `1.25`, and `1.50`:

```text
outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep_report.zip
```

## Listening Result

The perceptual result is negative:

- The alpha sweep is objectively measurable, but the rendered audio does not
  produce a clear perceptual timbre change as alpha changes.
- Target reconstruction does not sound like real singing. It sounds like a
  speech-like vocalization that has been stretched in time.
- Source articulation plus target embedding still sounds like the source speaker
  speaking; it does not create a convincing target singing timbre.
- Therefore the target-embedding oracle is not a useful perceptual upper bound
  inside the frozen ARTI-6 decoder.

## Interpretation

This is likely a model-path limitation, not just insufficient training data:

- ARTI-6 is a speech-oriented articulatory/synthesis model and does not carry a
  singing-capable melody/F0/prosody path through this demo.
- Singing quality depends on pitch trajectory, duration, breath, phonation,
  vocal effort, resonance changes, and musical timing. A shifted speaker
  embedding alone does not force the frozen ARTI-6 decoder to render those
  attributes.
- The current source-articulation setup reuses speech-like timing and content, so
  even a successful embedding shift is constrained to sound like speech.
- The ECAPA/ARTI-6 speaker embedding can move in vector space without producing
  an audible style or singing-domain change after decoding.

## Decision

Do not spend more time trying to make ARTI-6 produce the final audio demo.

Keep ARTI-6 outputs as:

- an engineering harness proving that paired data, embedding extraction, mapping,
  reporting, zipping, and subjective-eval pages work;
- a negative result showing that embedding-space movement is insufficient without
  a singing-aware decoder;
- an objective-diagnostic sandbox for speaker-domain metrics.

Move the actual audible demo to a model that explicitly supports singing or
speech-to-singing conversion.

## Next Direction

The next model path should satisfy these requirements before we invest in
training:

1. It must synthesize or convert singing-like audio, not only speech.
2. It must expose controllable speaker/timbre conditioning.
3. It must preserve or accept a singing pitch/prosody representation.
4. It must support same-speaker speech/singing or cross-domain conditioning.
5. It should still fit the existing harness shape: manifest in, comparative
   audio out, summary JSON, objective speaker-domain evaluation, subjective HTML,
   and portable zip.

Candidate families to evaluate next:

- singing voice conversion / singing voice synthesis models;
- speech-to-singing conversion models using music score or F0 control;
- audio foundation models with speaker conditioning and singing support;
- semantic-content models plus a singing-aware vocoder/acoustic model.

## Research Framing

This negative result is still useful. It supports a thesis claim that objective
embedding movement is not enough for cross-domain perceptual transfer. A credible
system needs an evaluation harness that combines:

- embedding-space movement;
- speaker-recognition robustness across speech/singing;
- perceptual listening ratings;
- a decoder capable of rendering singing-domain acoustic factors.
