# Literature Survey: Domain and Skill Shifters for Voice/Singing Conversion

## Goal

Create a literature survey that turns the current project direction into a ranked set of research options around lightweight domain/skill shifters for speech and singing conversion. The survey should help decide whether a Master's thesis direction can be built around freezing a strong backbone and training only a small shifter over speaker/style/prosody/representation space.

## What I Already Know

* The project is not continuing implementation right now; this task is a research handoff for another agent.
* The current hypothesis is: instead of retraining a full VC/SVC model, learn a lightweight shifter such as `z_shifted = z + f(z, domain, skill)`.
* The target domains include speaking vs. singing, novice vs. skilled voice performance, and dirty vs. clean recording conditions.
* Dataset-specific information such as microphone, environment, background music, and selected music style may leak into identity or style representations.
* Prior local ARTI-6 LinearVC experiments found that pure 6D articulatory LinearVC is not sufficient for full timbre conversion; ARTI-6 articulation is more defensible as a content/pronunciation/skill representation than as the main timbre conversion space.
* The user prefers deep-learning / representation-learning directions over pure DSP baselines.

## Key Local Context

* [`archive/demo_version_1_arti6_linearvc/context/arti6-linearvc-representation-audit-notes.md`](../../../archive/demo_version_1_arti6_linearvc/context/arti6-linearvc-representation-audit-notes.md) records the ARTI-6 LinearVC negative result and the pivot toward representation audits.
* [`archive/demo_version_1_arti6_linearvc/README.md`](../../../archive/demo_version_1_arti6_linearvc/README.md) summarizes the archived first-stage experiment.
* [`.trellis/tasks/archive/2026-05/05-22-cross-domain-timbre-shift/research/brainstorming_minutes.md`](../archive/2026-05/05-22-cross-domain-timbre-shift/research/brainstorming_minutes.md) records the previous agreement around latent-space steering and a micro-mapper.

## Research Questions

1. Can dataset-specific nuisance information such as mic, room, BGM, recording quality, and music style be separated from speaker identity or skill?
2. Is domain-adversarial training a good fit for dirty, mixed-source VC/SVC data?
3. What literature supports freezing a backbone and training only a lightweight shifter, adapter, mapper, or latent-space editor?
4. Can singing skill be represented as a latent attribute for novice-to-skilled conversion?
5. Can speaking skill be represented as a latent attribute for novice-to-skilled conversion?
6. Why is singing harder than speech conversion, especially at high F0 where spectral-envelope information is sparse?
7. How should a prosody prompt be prepared, and what is the minimum useful prompt granularity?
8. Where do articulatory representations help: timbre conversion, pronunciation editing, accent conversion, or skill correction?
9. How can we audit representation geometry to test whether singing identity space shrinks or differs from speaker space?
10. What evaluation protocol best fits dirty-data domain/skill conversion?

## Literature Survey Tasks

For each direction below, produce a focused mini-review.

### 1. Dataset-Specific Information as Nuisance

Research VC/SVC work that models or removes recording condition, microphone, room, background noise, BGM, source dataset, or music style.

Seed sources:

* Noise-robust voice conversion with domain adversarial training: https://arxiv.org/abs/2201.10693
* Noise-robust voice conversion with recording quality/environment latent variables: https://arxiv.org/abs/2406.07280

### 2. Domain-Adversarial Training for Dirty Voice Data

Research gradient reversal layers, domain classifiers, adversarial feature invariance, and disentanglement for noisy VC, TTS, speaker verification, ASR, and emotional VC.

Answer whether `dataset_id`, `mic_id`, `room_id`, `noise_type`, or `music_style` can be used as adversarial labels.

### 3. Frozen Backbone plus Lightweight Shifter

Research methods that avoid full model retraining: adapters, LoRA, embedding mappers, mean-delta steering, latent-space editing, training-free VC, kNN/retrieval VC, and codec/SSL-space conversion.

Seed sources:

* ContentVec: https://arxiv.org/abs/2204.09224
* kNN-VC: https://arxiv.org/abs/2305.18975

### 4. Singing Skill as a Latent Attribute

Research novice-to-skilled singing, singing voice beautification, singing technique control, style transfer, and amateur-to-professional conversion.

Focus on pitch accuracy, vibrato, breathiness, mixed voice, falsetto, rhythm, timing, and consonant/vowel clarity.

Seed sources:

* GTSinger: https://arxiv.org/abs/2409.13832
* CONTUNER: https://arxiv.org/abs/2404.19187
* TechSinger: https://arxiv.org/abs/2502.12572

### 5. Speaking Skill as a Latent Attribute

Research public-speaking style transfer, charismatic speech, speech coaching, fluency augmentation, pronunciation assessment, and prosodic competence.

Focus on pause, speech rate, pitch variety, prominence, clarity, confidence, and audience-facing delivery.

Seed sources:

* PSST public-speaking style transfer: https://aclanthology.org/2024.findings-emnlp.495/
* Public speaking coach review/system: https://link.springer.com/article/10.1007/s12369-025-01320-8

### 6. Why Singing Is Harder than Speech VC

Research high-F0 spectral envelope estimation, harmonic sparsity, formant ambiguity, long-vowel modeling, vibrato, breathiness, glissando, pitch/content/timbre disentanglement, and neural vocoder limitations for singing.

Seed sources:

* F0 transformation and high-F0 representation: https://www.mdpi.com/2078-2489/13/3/102
* Vocal tract resonances in speech and singing: https://pmc.ncbi.nlm.nih.gov/articles/PMC2689615/

### 7. Prompt-Based Prosody Transfer

Research one-shot/reference-prompt prosody transfer, speaker-dependent vs. speaker-independent prosody, prosody bottlenecks, and explicit prosody representations.

Answer how to prepare a prompt: sentence-level vs. phrase-level, same text vs. different text, and which features to extract from F0, energy, duration, pauses, rate, stress, and focus.

Seed sources:

* Wavelet analysis of speaker dependent and independent prosody for VC: https://www.isca-archive.org/interspeech_2018/sisman18b_interspeech.html
* PMVC: https://arxiv.org/abs/2308.11084
* Speech Prosody 2026 proceedings: https://www.isca-archive.org/speechprosody_2026/index.html

### 8. Articulatory Representation for Skill or Pronunciation Editing

Research articulatory coding, vocal-tract kinematics, EMA/ultrasound/silent speech, articulatory-to-speech synthesis, accent/pronunciation conversion, and RT-VC-style articulatory VC.

Answer whether articulation should be used for pronunciation/skill correction rather than timbre conversion.

Seed sources:

* Coding Speech through Vocal Tract Kinematics: https://arxiv.org/abs/2406.12998
* RT-VC: https://arxiv.org/abs/2506.10289

### 9. Representation Geometry Audit

Research methods for auditing what information exists in speech representations: linear probes, speaker/domain/style classifiers, PCA/UMAP, mutual information estimates, ABX tests, same-prompt cross-speaker distance, and layer-wise SSL analysis.

Target question: does singing identity space shrink, rotate, or become more entangled than speaker space?

### 10. Evaluation Protocol for Dirty-Data Skill/Domain Conversion

Research VCC/SVCC evaluation metrics and protocols for naturalness, speaker/singer similarity, content preservation, style similarity, prosody similarity, MOS/ABX tests, and objective metrics.

Seed source:

* Singing Voice Conversion Challenge 2025: https://vc-challenge.org/

## Required Output Format

Create one main report:

* `research/domain_skill_shifter_literature_survey.md`

The report should contain:

* Executive summary: 1-2 pages.
* Ranked recommendation: top 3 directions for a Master's thesis, with reasons.
* One section per direction, using the 10 directions above.
* For each direction:
  * 5-10 core papers, preferably sorted by year.
  * For each paper: task, data, representation, model/loss, evaluation, main conclusion.
  * How it supports or weakens the "only train a shifter" hypothesis.
  * Minimal experiment we could run in this repo or on Valkyrie.
  * Feasibility judgment: high / medium / low.
* Final synthesis:
  * Best thesis story.
  * Most defensible negative-result story.
  * Best demo-first story.
  * Which directions should be dropped.

## Acceptance Criteria

* [ ] The report covers all 10 directions.
* [ ] Each direction includes at least 5 relevant papers or clearly explains why fewer were found.
* [ ] Sources include links and enough citation metadata to find the paper again.
* [ ] The report explicitly ranks the top 3 directions.
* [ ] The report answers whether the "frozen backbone + lightweight shifter" framing is literature-supported.
* [ ] The report separates evidence from speculation.
* [ ] The report includes at least one minimal experiment proposal per direction.
* [ ] The report does not modify implementation code.

## Out of Scope

* Implementing models or experiments.
* Running training.
* Building a demo page.
* Changing existing ARTI-6 or Seed-VC scripts.
* Re-running previous LinearVC experiments unless only used as context.

## Handoff Prompt for the Next Agent

```text
Active task: .trellis/tasks/05-25-literature-domain-skill-shifters

You are taking over a literature survey task. Do not implement code. Read prd.md and the local context files referenced in "Key Local Context". Then perform the literature survey described in "Literature Survey Tasks".

Write the final survey to:
  .trellis/tasks/05-25-literature-domain-skill-shifters/research/domain_skill_shifter_literature_survey.md

The deliverable must cover all 10 directions, include citations/links, rank the top 3 thesis directions, and explicitly evaluate whether "freeze a strong backbone and train only a lightweight shifter" is supported by the literature.
```

