# Complete Pro Model Question Pack

Date: 2026-06-08

These are standalone prompts for asking a stronger Pro model in parallel. Each
prompt includes its own context, so you can paste any one of them into a fresh
chat without sending the rest.

Recommended order if you only ask a few:

1. Prompt A: field zeitgeist and good directions.
2. Prompt B: full review/design of the current timbre-shift paper idea.
3. Prompt C: singing skill evaluation reality check.
4. Prompt D: advisor-style decision and 30-day plan.

## Prompt A: Field Zeitgeist And Good Research Directions

I am a master's student exploring speech/singing voice research. I only have a
few GPUs, so I cannot train a new foundation model or do scaling-heavy singing
voice conversion. I want a research direction that is novel enough, interesting,
and feasible.

My broad interests:

- same-person timbre or vocal identity shift between speaking and singing;
- same-person timbre shift across languages, if data makes this possible;
- speaker/timbre/content/prosody disentanglement in speech or singing;
- probing and steering directions in frozen SSL/audio-codec representations;
- singing style or technique control, such as vibrato, breathiness, falsetto,
  glissando, belting, mixed voice, and other singing techniques;
- automatic singing quality or skill evaluation, if it can be formulated
  rigorously.

Please act as a senior researcher and give me a 2024-2026 field map for:

- singing voice conversion;
- singing style conversion;
- speech-to-singing or singing-to-speech conversion;
- cross-lingual speaker/timbre disentanglement;
- SSL/audio-codec representation factorization;
- singing quality, skill, or technique evaluation.

I need you to be critical and source-grounded. Please use primary sources where
possible: papers, official challenge pages, datasets, code repositories, and
proceedings.

Please answer:

1. What is the current zeitgeist? What are people excited about now?
2. What claims are saturated or no longer novel?
3. What problems remain clearly unsolved?
4. Which labs, groups, datasets, benchmarks, and challenges are central?
5. Which 15-25 papers/systems should I read first?
6. Which systems have usable code/checkpoints and which are paper-only?
7. What research questions fit a small-GPU master's project?
8. Which directions are likely too risky, too incremental, or too engineering-only?

Then produce a ranked list of 8-12 possible research directions. For each
direction, include:

- one-sentence research question;
- why it matters now;
- expected novelty;
- key related work;
- dataset needed;
- baseline needed;
- minimum experiment;
- expected compute;
- likely failure mode;
- whether I should pursue, park, or reject it.

Output should include:

- a concise executive summary;
- a table of key papers/systems;
- a table ranking research directions;
- a short reading list grouped by topic;
- explicit warnings about overclaims.

## Prompt B: Full Review And Experiment Design For My Current Paper Idea

I am considering one specific paper/thesis idea. Please evaluate it as if you
were both a harsh reviewer and a practical advisor.

Context:

I am studying same-person speech-vs-singing timbre or vocal identity shift. The
intuition is that a speaker/singer does not have one static speaker identity
embedding. The same person may have a stable identity core plus a vocal-mode
specific residual: their speaking voice and singing voice are related, but not
identical. If we can model that residual, it may help singing voice conversion
when we only have target speech reference and no target singing reference.

Constraints:

- I only have a few GPUs.
- I cannot train a large SVC/codec/foundation model from scratch.
- I prefer frozen-model analysis, small learned heads, small adapters, and
  rigorous evaluation.
- I want a paper-worthy research question, not just an engineering demo.

Candidate data:

- GTSinger, because it has paired speech/singing, phoneme alignments, singing
  technique labels, and 20 professional singers.
- I know GTSinger is not enough for causal same-speaker language
  disentanglement because singer and language are confounded.

Candidate models/features:

- WavLM Base+ hidden layers, possibly layers 3/6/9/12;
- ContentVec if useful;
- ECAPA-TDNN as a speaker verification baseline/evaluator;
- FACodec / NaturalSpeech 3 streams as a factorized-codec comparison;
- Seed-VC as downstream zero-shot SVC baseline;
- kNN-VC or FreeSVC as possible no-training or open baselines.

Candidate hypothesis:

Frozen SSL/audio-codec features contain separable evidence for:

- stable identity core;
- speech/singing vocal-mode residual;
- content/phone information;
- F0/prosody/energy;
- singing technique/style.

Candidate pipeline:

1. Stage A: no synthesis. Cache frozen features and build a leakage map across
   layers, temporal statistics, and codec streams.
2. Stage B: train small heads over frozen features to separate `z_core` and
   `z_mode`.
3. Stage C: use the learned representation or residual to improve downstream
   Seed-VC conditioning when only target speech reference is available.

I need you to produce a complete research review and experiment plan. Please
answer all of the following in one coherent response.

Part 1: Kill Or Improve The Idea

1. Is this idea good, mediocre, or bad?
2. What exactly is not novel? Discuss AdaIN-VC, LoIN, FACodec/NaturalSpeech 3,
   FreeCodec, MSR-Codec, Seed-VC, GTSinger, SVCC 2025, and recent speaker
   leakage probing work where relevant.
3. What is the strongest honest novelty framing?
4. What claims should I avoid?
5. What would Reviewer 2 attack?
6. What would make the idea publishable rather than just a probe study?

Part 2: Novelty Matrix

Build a novelty matrix comparing my idea against prior work. Include columns
for:

- global mean/std or instance statistics;
- local/multiscale temporal statistics;
- factorized content/prosody/timbre/residual codecs;
- speaker leakage probing in SSL features;
- same-person speech-vs-singing identity shift;
- phone/F0/duration-controlled analysis;
- unseen-singer evaluation;
- downstream SVC conditioning intervention;
- public code/data feasibility.

Then identify the one or two defensible contribution claims.

Part 3: Stage A Experiment Design

Design the frozen-feature audit in engineering-ready detail:

1. exact dataset split strategy;
2. segment/example construction;
3. feature cache schema;
4. representation variants;
5. temporal statistics or multiscale bands;
6. probe targets;
7. metrics;
8. negative controls;
9. cheap acoustic shortcut baselines;
10. F0, phone, duration, song/take, SNR, singer, and language controls;
11. statistical analysis plan, including bootstrap or mixed-effects modeling;
12. stop/go criteria for moving to Stage B;
13. expected compute and storage.

Important: explain how to avoid confusing probe recoverability with true
disentanglement.

Part 4: Stage B And Stage C Design

Assume Stage A finds real signal. Design the intervention:

1. how to define `z_core` and `z_mode`;
2. losses that are justified and losses that are risky;
3. mandatory baselines;
4. how to distinguish oracle residual from deployable residual;
5. how to avoid requiring target singing at inference;
6. where, if anywhere, to intervene in Seed-VC conditioning;
7. objective metrics;
8. subjective evaluation design;
9. what counts as success;
10. what failure result could still be publishable.

Part 5: Baseline And Code Feasibility

Audit these candidates and decide whether each is core baseline, optional
baseline, or reference only:

- WavLM Base+ / Large;
- ContentVec;
- ECAPA-TDNN;
- FACodec / NaturalSpeech 3;
- Seed-VC;
- kNN-VC;
- FreeSVC;
- Serenade;
- Vevo/Amphion;
- HQ-SVC;
- RVC / DDSP-SVC / so-vits-svc.

For each, state whether public code/checkpoints are actually usable, whether
target-speaker training is required, and what compute/environment risk it adds.

Part 6: AI-Coding And Engineering Checkpoints

I want to use AI coding agents to implement the experiments without hallucinated
or misaligned code. Define:

1. task decomposition;
2. file/artifact contracts;
3. manifest schema;
4. split invariants;
5. feature-cache schema;
6. smoke tests;
7. unit/integration tests;
8. result table format;
9. reproducibility requirements;
10. failure modes that must block progress.

Write this as a spec I could hand to a coding agent.

Part 7: Paper Strategy

Assume results are modest but real. Propose:

1. possible paper titles;
2. abstract structure;
3. contribution bullets;
4. related work organization;
5. method section outline;
6. experiment tables and figures;
7. ablations;
8. limitations;
9. strongest narrative if results are positive;
10. strongest narrative if results are mixed;
11. claims to avoid.

Part 8: Final Decision

End with:

- go/no-go recommendation;
- the first experiment I should run this week;
- the result that would make you continue;
- the result that would make you pivot;
- a 30-day plan.

Please be blunt, concrete, and source-grounded. Distinguish verified facts from
speculation.

## Prompt C: Singing Skill Evaluation Reality Check And Experiment Design

I am considering a second research direction: automatic singing skill or singing
quality evaluation.

Original vague idea:

Can we predict how skilled a singer is from audio? Can we predict what a person
would sound like after becoming more professional at singing?

I suspect the "future professional voice" target may not be valid because there
is no obvious longitudinal ground truth. I want you to reformulate this into
researchable tasks if possible.

Constraints:

- I only have a few GPUs.
- I prefer small models, frozen embeddings, interpretable features, or
  benchmark/evaluation work over training a large audio model.
- I care about useful singing feedback, not just a number.
- I want to know whether this can be a real paper or only a product idea.

Please give a complete review and experiment plan.

Part 1: Reality Check

1. Is "predict future professional voice" a valid supervised learning target?
2. What kind of ground truth would be required to make it valid?
3. What public datasets actually support instead: current quality, MOS,
   technique labels, reference-match correctness, pairwise improvement, or
   multi-dimensional feedback?
4. What claims should I avoid?

Part 2: Dataset Survey

Compare these datasets/sources where relevant:

- SingMOS-Pro;
- SingMOS-v1;
- GTSinger;
- VocalSet;
- SVQTD;
- Lyra-SA;
- PESnQ / SingEval / AME430;
- VocalVerse / QwenFeat-Vocal-Score;
- TG-Critic;
- 10KSinging;
- Learn-by-Referencing / ranking-based singing assessment;
- MFFMOS / GOSMOS;
- classic Nakano / MiruSinger work;
- any Waseda/Nakano/Goto/Hiraga karaoke or singing assessment work that is
  relevant.

For each, state:

- labels;
- access;
- code availability;
- best use;
- leakage risks;
- whether it is suitable for a small-GPU project.

Part 3: Task Formulations

Design rigorous alternatives to "future professional potential":

1. no-reference current singing quality;
2. reference-conditioned karaoke pitch/rhythm/lyric scoring;
3. singing technique or vocal-attribute recognition;
4. multi-dimensional feedback for pitch, rhythm, timbre, breath, emotion, and
   technique;
5. pairwise improvement ranking across takes.

For each, give:

- why it matters;
- dataset;
- baselines;
- metrics;
- split strategy;
- expected compute;
- scientific risk;
- product/usefulness risk.

Part 4: Karaoke Scoring Traps

Explain how a karaoke scoring model can be wrong or misleading. Include:

- punishment of expressive deviation;
- accompaniment/source-separation leakage;
- popularity and platform bias;
- song difficulty;
- singer identity leakage;
- generated-vocal versus real-amateur domain shift;
- mismatch between pitch accuracy and musical quality.

Part 5: Three Small-GPU Experiments

Design three concrete experiments I could run:

1. one safest benchmark experiment;
2. one more novel technique/feedback experiment;
3. one risky but interesting experiment.

For each, include data, features, model, metrics, controls, expected compute,
minimum publishable result, and failure interpretation.

Part 6: Final Recommendation

Should I pursue singing skill evaluation as my main thesis direction, a backup
direction, or not at all? Compare it against the speech/singing timbre-shift
idea. End with a go/no-go recommendation and a 30-day plan.

Please be strict and source-grounded.

## Prompt D: Advisor-Style Direction Choice And 30-Day Plan

Act as my research advisor. I have limited compute, a few GPUs, and I want a
master's-level project in speech/singing voice research. I care about
representation learning, timbre shift, probing/steering, singing voice
conversion, and possibly singing skill evaluation. I need a direction that is
novel, feasible, and educational.

Candidate directions:

1. Same-person speech-vs-singing timbre shift:
   frozen SSL/audio-codec leakage map, stable identity core, mode residual, and
   downstream Seed-VC intervention.
2. Singing style or technique direction discovery:
   find and possibly steer directions for vibrato, breathiness, falsetto,
   glissando, etc.
3. Objective evaluation metrics for singing style conversion:
   correlate automatic metrics/probes with SVCC-style subjective goals.
4. Cross-lingual timbre leakage or stress test:
   test speaker/language entanglement, but only if data supports the claim.
5. Singing quality/skill/technique evaluator:
   MOS, reference-conditioned karaoke scoring, technique recognition, or
   multi-dimensional feedback.
6. Robustness to separated-vocal artifacts and noisy web singing data:
   source-separation/noise/F0 perturbation stress tests for SVC or evaluators.

Please:

1. Rank these directions by novelty, feasibility, data availability, code
   availability, publishability, and fit to the 2024-2026 field zeitgeist.
2. Identify which direction you would force me to pursue first and why.
3. Identify one backup direction.
4. Give the single experiment I should run this week.
5. Give the result that would convince you to continue.
6. Give the result that would make you pivot.
7. Give the one paper or benchmark I should imitate structurally.
8. Give the one overclaim you would forbid.
9. Give a 30-day plan with weekly deliverables.
10. Give a list of questions I should ask another Pro model to double-check
    your advice.

Be blunt and concrete. I prefer honest negative feedback over vague optimism.

## Prompt E: Citation-Chaining Literature Task

I want to understand the literature around speech/singing voice representation,
conversion, disentanglement, and evaluation. Please do citation chaining from
these anchors:

- GTSinger;
- Seed-VC;
- FACodec / NaturalSpeech 3;
- SVCC 2025;
- LoIN;
- AdaIN-VC;
- FreeCodec;
- MSR-Codec;
- speaker leakage probing in SSL speech representations;
- SingMOS-Pro or other singing quality assessment papers.

My constraints:

- I only have a few GPUs.
- I need papers that help design a feasible experiment, not just impressively
  large models.
- I care about public code/data and experimental patterns.

For each anchor:

1. summarize the anchor paper/system;
2. list the most relevant cited works;
3. list the most relevant citing works;
4. identify the experiment-design pattern it teaches;
5. identify what it already solves;
6. identify what gap remains;
7. say whether it is experiment-critical, baseline candidate, related-work
   context, or not useful.

Then synthesize:

- the top 20 papers I should read;
- the top 8 experiment patterns I should imitate;
- the strongest novelty gaps left;
- the papers with usable public code/data;
- the papers that are important but too expensive or unreproducible for me.

Please cite sources and distinguish verified facts from speculation.

## Prompt F: Research Process Tutorial Using My Case

I want to learn how to do this kind of ML/audio research properly. Use my
speech/singing timbre-shift idea as the running example.

Idea:

Use frozen speech/audio representations to study same-person speech-vs-singing
identity shift, then maybe improve speech-reference singing voice conversion by
modeling a stable identity core plus a mode-specific residual.

Constraints:

- few GPUs;
- need novelty;
- need careful experiments;
- want to use AI coding agents without letting them hallucinate;
- want to learn the whole research process from idea to paper.

Please teach the entire workflow:

1. how to turn a vague intuition into a research question;
2. how to scan literature;
3. how to build a novelty matrix;
4. how to choose data;
5. how to choose baselines;
6. how to write hypotheses;
7. how to design a pilot;
8. how to detect confounds;
9. how to design the main experiment;
10. how to plan ablations;
11. how to design downstream intervention;
12. how to decide whether subjective evaluation is needed;
13. how to interpret mixed results;
14. how to write honest claims;
15. how to decide whether to pivot.

For each step, include:

- concrete deliverable;
- example for my case;
- bad version;
- good version;
- what an AI coding/research assistant can help with;
- what I must verify myself.

End with a template checklist I can reuse for future research ideas.

