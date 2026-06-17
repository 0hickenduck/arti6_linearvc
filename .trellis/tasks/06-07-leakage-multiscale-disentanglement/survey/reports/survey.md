# Survey

- Date: 2026-06-08
- Task: 06-07-leakage-multiscale-disentanglement

## Human-Readable Synthesis

The current speech/singing voice field is converging on a few clear themes:
zero-shot conversion, singing style conversion, robust conversion from imperfect
vocals, and explicit representation factorization. The most important 2025-2026
signal is SVCC 2025: singer identity conversion is no longer enough. The harder
and more publishable problem is preserving identity and content while controlling
dynamic singing style, especially breathy, glissando, vibrato, and related
phonation/prosody effects.

For this task, the strongest small-GPU research lane is a representation audit
plus intervention, not a new full SVC foundation model. GTSinger gives paired
speech/singing, phoneme alignments, technique labels, and singer-disjoint
evaluation. Seed-VC, FACodec, FreeSVC, Serenade, and Vevo/HQ-SVC inference give
enough open baselines to make the work grounded. The novelty should be a
controlled leakage map across SSL/codec layers and temporal bands, followed by a
small residual or conditioning intervention that improves a real downstream
metric on held-out singers.

Open-source availability is the benchmark gate. GTSinger, Seed-VC, FACodec,
FreeSVC, Serenade, and HQ-SVC inference are usable. S2Voice, DAFMSVC, R2-SVC,
and singing-to-speech flow are important references but are survey/reference
only by default because no usable official code was identified in this pass.

The main overclaim to avoid is language disentanglement from GTSinger. GTSinger
is excellent for speech-versus-singing and technique analysis, but singer and
language are confounded. Use it for vocal-mode/timbre shift, not for causal
same-speaker multilingual identity claims.

Detailed field map:
`survey/reports/field-map-2024-2026.md`

Detailed paper extraction:
`survey/papers/key-paper-extractions-2024-2026.md`

## Open Questions

- Which frozen encoders should be fixed for Stage A: WavLM plus FACodec only, or
  add Whisper/ContentVec because Seed-VC and FreeSVC rely on those families?
- Should the first downstream intervention target cross-mode speaker
  verification, Seed-VC target similarity, or technique/style disentanglement?
- What subjective-evaluation budget is realistic if Stage B reaches synthesis?

## Addendum: Singing Skill Evaluation

Full report: `survey/reports/singing-skill-evaluation.md`

Singing skill is researchable, but "future professional potential" is not a
valid public benchmark target without longitudinal outcomes. Existing datasets
mostly support current perceived quality, reference-conditioned karaoke
correctness, vocal technique/attribute detection, and multi-dimensional feedback.

The practical benchmark shape is a multi-head evaluator: no-reference MOS/rank,
reference-conditioned pitch/rhythm diagnostics when a score or MIDI exists,
technique/attribute probes, and optional timbre/breath/emotion/technique
dimension scores. It must include leakage controls for singer identity, song,
recording path, accompaniment, source separation, generated-system origin, and
dataset source.

Usable benchmark candidates are SingMOS/SingMOS-Pro, GTSinger, VocalSet,
PESnQ/SingEval/AME430 with audio-access caveats, and VocalVerse only with
compute/license caution. TG-Critic, 10KSinging, Learn by Referencing, MFFMOS, and
Nakano/MiruSinger are survey/reference by default unless their missing runnable
code/data gaps are closed.
