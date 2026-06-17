# Research Agenda and Candidate Tracks

Research update: 2026-06-08.

## User Intent

The user wants a strong research assistant for speech and singing voice
research, not merely a coding agent. The assistant should:

- survey current literature and top conference directions;
- identify strong labs, benchmarks, datasets, and best-performing systems;
- ask research-design questions that sharpen vague intuitions into tractable
  experiments;
- connect field trends to the user's concrete interests: cross-language and
  speech/singing timbre shift, latent probing or steering directions, and
  automatic singing skill evaluation.

## Existing Local Context

- Prior notes frame the user's core insight as natural timbre shift: the same
  person may sound different when switching languages or moving between
  speaking and singing.
- Prior notes also record a methodological preference for deep-learning
  representation learning, probing, and lightweight learned mappers over
  classical DSP-only baselines.
- The current PRD already turns one part of that idea into an executable
  Stage-A audit: frozen SSL and factorized-codec features, multiscale temporal
  decomposition, leakage probes, and speech/singing identity-gap analysis.
- Existing experiments already show a cross-domain verification gap and include
  Seed-VC/GTSinger pipelines, global shift baselines, and residual mapper
  baselines.

## Candidate Track A: Same-Person Timbre Shift

Core question:

> How does a speaker/singer's acoustic identity move when vocal mode or
> language changes, and can that movement be represented as a controllable
> residual rather than treated as unwanted leakage?

Near-term tractable version:

- use GTSinger for speech-versus-singing;
- keep multilingual claims as future work because GTSinger confounds speaker
  and language;
- map where speaker, vocal mode, F0, content, and technique are recoverable
  across layers and temporal bands;
- test whether a stable identity core plus mode-specific residual improves
  cross-mode identity verification and later Seed-VC conditioning.

Good research posture:

- do not claim a universal "timbre direction" until it generalizes to unseen
  singers;
- distinguish diagnostic probe evidence from causal synthesis evidence;
- explicitly control F0, phonetic identity, duration, song, and recording
  condition.

## Candidate Track B: Latent Probing and Skill/Style Directions

Core question:

> Can we discover interpretable directions for singing-related attributes such
> as voicing, breathiness, vibrato, belt, falsetto, or technique, and can those
> directions be steered without damaging identity/content?

Near-term tractable version:

- start with labeled technique recognition or technique-conditioned probing;
- use GTSinger's technique annotations as a controlled entry point;
- compare linear directions, nonlinear probes, and causal interventions in a
  frozen codec or SVC conditioning space.

Good research posture:

- treat "direction" as an empirical object with preservation metrics, not just
  a visually appealing latent-vector analogy;
- report steering efficiency versus identity/content preservation;
- avoid overclaiming if the direction is singer-, pitch-, or language-specific.

## Candidate Track C: Singing Skill Evaluation

Core question:

> Can a model score or diagnose singing ability from audio in a way that is
> useful for learning or synthesis, even without true longitudinal ground truth
> for how a person sounds after becoming professional?

The direct "predict future professional version of this singer" target is weak
because there is usually no paired before/after ground truth. More defensible
proxy formulations:

1. Technique-specific scoring:
   classify or regress one narrow technique such as vibrato control, pitch
   stability, breathiness, belting, falsetto, or note transition cleanliness.
2. Reference-based karaoke assessment:
   compare a singer's pitch, rhythm, lyric alignment, and expression against a
   known score/reference, while acknowledging that professional singers may
   intentionally deviate.
3. Listener-quality prediction:
   predict MOS or expert ratings of singing naturalness/quality rather than
   "skill" as a single latent truth.
4. Improvement-direction modeling:
   produce diagnostic feedback vectors, such as "more stable F0", "less
   pressed phonation", or "cleaner vibrato onset", without claiming to generate
   the future professional voice.

Relevant current anchors from quick search:

- GTSinger provides 80.59 hours of multilingual professional singing, 16.16
  hours of paired speech, phoneme alignments, music scores, and annotations for
  six singing techniques.
- SingMOS-Pro is a recent dataset/benchmark for automatic singing quality
  assessment with MOS annotations.
- Classic singing skill evaluation work already used pitch interval accuracy
  and vibrato features without requiring score information for the sung melody.
- Waseda-related public search results found karaoke contests and a Waseda
  publication on parody detection/alignment collapse in karaoke singing, but no
  confirmed public "Waseda karaoke skill dataset" in the quick pass.

## Survey Questions To Answer Next

1. What are the strongest 2024-2026 papers and challenges for singing voice
   conversion, singing style conversion, and speech/singing conversion?
2. Which recent systems are actually usable as baselines because code and
   pretrained checkpoints are public?
3. Which datasets support same-person speech/singing, multilingual
   same-person voice, singing technique labels, MOS/skill labels, or
   reference-based karaoke scoring?
4. Is the user's most defensible thesis contribution a new representation
   analysis, a controllable intervention method, a benchmark/evaluation
   protocol, or an application-oriented singing skill assessor?

## Sources From Quick External Search

- GTSinger paper: https://arxiv.org/abs/2409.13832
- GTSinger NeurIPS proceedings: https://proceedings.neurips.cc/paper_files/paper/2024/hash/023d2c1a17cf35b11a0cbb43a0677c91-Abstract-Datasets_and_Benchmarks_Track.html
- SingMOS-Pro dataset: https://huggingface.co/datasets/TangRain/SingMOS-Pro
- SingMOS-Pro paper: https://arxiv.org/abs/2510.01812
- Singing Voice Conversion Challenge 2025: https://vc-challenge.org/
- SVCC 2025 paper: https://arxiv.org/abs/2509.15629
- HQ-SVC AAAI 2026: https://ojs.aaai.org/index.php/AAAI/article/view/40249
- DAFMSVC Interspeech 2025: https://www.isca-archive.org/interspeech_2025/chen25d_interspeech.html
- Singing-to-speech conversion, 2025: https://link.springer.com/article/10.1186/s13636-025-00400-x
- Classic singing skill evaluation: https://www.isca-archive.org/interspeech_2006/nakano06_interspeech.html
- Waseda karaoke/parody detection record:
  https://waseda.elsevierpure.com/en/publications/spotting-parodies-detecting-alignment-collapse-between-lyrics-and/
