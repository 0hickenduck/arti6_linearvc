# Leakage and Multiscale Disentanglement Study

## Goal

Determine whether a multiscale temporal-statistical decomposition of frozen
speech representations can separate stable speaker identity from
speech/singing vocal-mode residuals, and whether that separation is sufficiently
novel and effective to justify integration into the project's Seed-VC path.

## What I Already Know

- The repository already demonstrates a speech/singing speaker-embedding gap:
  speech-to-speech identification is 95% with EER 0.024, while
  speech-to-singing identification is 70% with EER 0.125.
- Existing repository experiments include a global difference-of-means shift,
  a residual MLP mapper, Seed-VC speech/singing prompt comparisons, and a
  GTSinger paired-data pipeline.
- GTSinger provides paired speech/singing and suitable singer-disjoint
  evaluation, but does not independently support language-leakage claims.
- Mean/std normalization, residual streams, factorized codecs, and leakage
  probes all have prior art.
- The candidate novelty is their controlled combination around
  speech-versus-singing identity and a downstream unseen-singer intervention.
- The user wants the project to support a broader research-advisory workflow:
  source-grounded literature survey, current conference/best-result tracking,
  and concrete research-question design rather than only implementation.
- The user's current research taste favors deep-learning representation
  learning and probing over pure DSP-only approaches.
- A second candidate direction is automatic singing skill or technique
  evaluation: predicting quality, technique control, or improvement direction
  from audio when professional-growth ground truth is unavailable.

## Requirements (Evolving)

- Build a source-grounded novelty matrix before implementation.
- Maintain a research-agenda layer that separates near-term executable
  experiments from broader field survey and thesis-positioning questions.
- Use speaker-disjoint and song-aware evaluation.
- Audit both linear and nonlinear factor recoverability.
- Compare global statistics against nonredundant temporal bands.
- Select temporal scales through a logarithmic sweep and empirical probes,
  using linguistic timescales only as interpretation priors.
- Control the speech/singing identity gap for phone identity, phone duration,
  F0, and transition/coarticulation effects.
- Include existing repository methods as baselines.
- Separate diagnostic probing from causal swapping/intervention evidence.
- Gate expensive synthesis work on a successful frozen-feature audit.
- Avoid language-disentanglement claims until same-speaker multilingual data is
  available and controlled.
- Treat singing skill evaluation as a separate candidate track unless the user
  explicitly chooses to fold it into the current timbre-shift experiment.

## Acceptance Criteria (Evolving)

- [x] Closest prior work and overlap boundaries are documented.
- [x] A concrete staged experiment is specified.
- [ ] The user chooses the initial experimental scope.
- [ ] Exact encoder checkpoints and resource budget are fixed.
- [ ] Implementation plan and task context are finalized.
- [ ] Stage A produces reproducible split manifests and a leakage cube.
- [ ] Results determine whether Stage B should proceed.

## Recommended MVP

Stage A only:

1. GTSinger.
2. WavLM plus pretrained FACodec.
3. Five singer-disjoint folds.
4. Global mean/std and a 20–1280 ms logarithmic temporal-scale sweep.
5. Linear and MLP probes for vocal mode, speaker, F0/energy, phonetic content,
   and singing technique.
6. A phone-conditioned identity-gap analysis beginning with aligned vowels.
7. No new codec and no Seed-VC modification until the stop/go criteria pass.

## Out of Scope for MVP

- Training a neural codec from scratch.
- Claiming language disentanglement from GTSinger.
- Treating VTuber web audio as controlled quantitative ground truth.
- Large subjective listening studies.
- Fine-tuning the SSL backbone before frozen-feature results justify it.
- Predicting a singer's future professional voice as a direct supervised target
  before a defensible proxy label, rubric, or longitudinal dataset is found.

## Research References

- [Prior-work novelty map](research/prior-work-novelty-map.md)
- [Specific experiment protocol](research/experiment-protocol.md)
- [Temporal scales, F0, and phonetic gap](research/timescale-and-phonetic-gap.md)
- [Research agenda and candidate tracks](research/research-agenda.md)
- [2024-2026 field map](survey/reports/field-map-2024-2026.md)
- [Current idea review](survey/reports/current-idea-review.md)
- [Singing skill evaluation survey](survey/reports/singing-skill-evaluation.md)
- [Feasible baselines and compute plan](survey/reports/feasible-baselines-and-compute.md)
- [Pro model question pack](survey/reports/pro-model-question-pack.md)
- [Pro4/Pro5 learning synthesis](survey/reports/pro4-pro5-learning.md)
- [Teacher meeting cheat sheet, 2026-06-17](survey/reports/teacher-cheatsheet-2026-06-17.md)
- [Teacher meeting screen sketch, 2026-06-17](survey/reports/teacher-screen-sketch-2026-06-17.md)
- [Teacher meeting architecture addendum, 2026-06-17](survey/reports/teacher-architecture-addendum-2026-06-17.md)
- [Teacher meeting final notes, 2026-06-17](survey/reports/teacher-meeting-final-2026-06-17.md)
- [Design clarification: technique vs timbre tracks, 2026-06-17](survey/reports/design-clarification-2026-06-17.md)

## Technical Notes

- Existing paired-data preparation:
  `arti6_linearvc_demo/prepare_gtsinger_tiny.py`.
- Existing cross-domain evaluation:
  `arti6_linearvc_demo/run_speaker_domain_eval.py`.
- Existing results and commands:
  `arti6_linearvc_demo/README.md`.
- FACodec is the strongest immediately reusable factorized-codec comparison
  because pretrained weights and implementation are public.
- Pro5 is the recommended next learning/report focus because it directly
  ranks the research lanes and gives a 30-day plan for the speech/singing
  timbre-shift MVP. Pro4 should be used as a backup-track guardrail for
  singing skill or feedback evaluation, not as the main thesis direction yet.
- For the 2026-06-17 teacher meeting, present two directions clearly:
  GTSinger technique/style control as a backup or parallel pilot, and
  same-person speech-vs-singing timbre shift as the main thesis candidate.
- The simplified screen-share version should emphasize two uncertainties:
  controlling F0/duration without erasing real timbre, and testing whether
  singing technique information is linear or requires nonlinear adapters.
- GRL/LoRA should be presented as an architecture-stage option after the
  frozen-feature audit, not as a replacement for residualization. It needs a
  target-preservation loss plus a nuisance adversary and must be compared
  against simpler controls.
- The canonical teacher-facing file is
  `survey/reports/teacher-meeting-final-2026-06-17.md`; earlier teacher files
  are draft/reference versions with more detail.
- The technique-adaptation track remains under-specified beyond probing; it
  needs a base generator, input/output contract, losses, and evaluation before
  it can become an adapter/generation project. The timbre-residual track has a
  clearer Pro-designed Stage A/B/C path.

## Open Question

- Should the next planning milestone convert Pro5 into an engineering-ready
  Stage A experiment spec, or pause to fully design the Pro4 singing
  feedback/technique backup track first?
