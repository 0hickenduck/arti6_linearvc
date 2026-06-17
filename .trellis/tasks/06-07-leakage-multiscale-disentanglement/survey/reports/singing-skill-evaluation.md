# Singing Skill Evaluation Survey

- Date: 2026-06-08
- Task: 06-07-leakage-multiscale-disentanglement
- Scope: feasibility of evaluating singing skill, usable datasets, labels,
  metrics, baselines, karaoke-score traps, and small-GPU experiment designs.

## Bottom Line

Singing skill can be evaluated in researchable ways, but "will this singer become
professional?" is not a well-posed benchmark unless the project has longitudinal
outcomes such as future teacher ratings, audition results, training history, or
career outcomes. Public datasets mostly measure current perceived quality,
reference-match correctness, technique presence, or expert/ordinary-listener
rubrics. They do not provide future-potential ground truth.

The best task formulation is therefore:

> Estimate current singing quality and diagnose improvement-relevant dimensions,
> while reporting uncertainty and avoiding claims about future professional
> potential.

The strongest practical path is a multi-head evaluator:

1. No-reference current-quality score or rank.
2. Reference-conditioned pitch/rhythm alignment when MIDI/lyrics/reference are
   available.
3. Technique and vocal-attribute detectors.
4. Dimension-level feedback for timbre, breath, emotion, and technique where
   labels exist.

Use open-code baselines first: SingMOS/SingMOS-Pro, GTSinger, VocalSet,
PESnQ/SingEval/AME430 if audio access is solved, and VocalVerse only if the
compute/license constraints are acceptable. Treat TG-Critic, 10KSinging, Learn by
Referencing, MFFMOS/GOSMOS, and the classic Nakano/MiruSinger line as
survey/reference unless code and data are verified.

## Feasible Task Formulations

### 1. Current Perceived Quality

Predict a MOS-like or rank-like score from audio alone. This is the closest
answer to "how good does this singing sound now?" It can use SingMOS-Pro,
SingMOS-v1, VocalVerse labels, TG-Critic labels, or SingEval annotations.

Good outputs:

- scalar MOS with confidence interval;
- percentile/rank against a defined reference population;
- pairwise preference: "take A is likely better than take B";
- calibration notes by song, singer, language, and recording condition.

This should not be sold as future potential. It is current perception under a
given listener population and dataset distribution.

### 2. Reference-Conditioned Karaoke Assessment

Compare a performance to a song-specific reference: MIDI, lyrics, reference
singing, or score. This is appropriate for karaoke, sight-singing, or practice
feedback. Lyra-SA, PESnQ, and the Learn by Referencing line are the closest
sources.

Good outputs:

- pitch alignment and pitch-stability errors;
- rhythm/tempo alignment;
- lyric/phoneme timing where alignments exist;
- sections with the largest deviations.

The trap is that reference matching can punish stylistic freedom, ornamentation,
transposition, expressive timing, and valid vibrato. It is useful as a practice
metric, not as a complete definition of artistic quality.

### 3. Technique and Attribute Recognition

Classify or score observable vocal behaviors: vibrato, falsetto, breathiness,
glissando, pharyngeal voice, resonance/placement labels, roughness, openness, and
similar features. GTSinger, VocalSet, and SVQTD are the strongest sources.

Good outputs:

- binary or ordinal technique labels;
- confidence per segment;
- time-localized detections;
- confusion-aware feedback, especially for similar classes such as straight tone
  versus vibrato.

This is not an overall skill score. A beginner can use a technique poorly, and a
professional can choose not to use it.

### 4. Explainable Multi-Dimensional Scoring

Predict component scores and comments: timbre, breath control, emotion,
technique, pitch, rhythm, and overall quality. VocalVerse/Sing-MD, SVQTD,
PESnQ/SingEval, and APSIPA 2021 explainable SQA are the useful references.

Good outputs:

- dimension scores with evidence snippets;
- top weak dimensions;
- pairwise improvement across repeated takes;
- optional natural-language critique, only after calibrated dimensions are
  reliable.

This is the most product-relevant formulation for coaching, but it requires
careful label provenance and should separate expert-rubric labels from ordinary
listener preference labels.

### 5. Longitudinal Improvement and Future Potential

This is feasible only with longitudinal data. A valid dataset would need repeated
recordings from the same singer, training exposure, teacher comments, and future
outcomes. Existing public datasets do not provide this. A small study can still
measure "short-term improvement potential" by collecting two or more takes after
feedback and labeling which take improved.

## Dataset and Baseline Map

| Source | Audio and labels | Access | Code gate | Best use | Caveats |
| --- | --- | --- | --- | --- | --- |
| [SingMOS-Pro](https://arxiv.org/abs/2510.01812), [dataset](https://huggingface.co/datasets/TangRain/SingMOS-Pro), [code](https://github.com/South-Twilight/SingMOS) | 7,981 Chinese/Japanese vocal clips, 11.15h, 41 generated systems across 12 datasets, at least five experienced annotators per clip, utterance/system MOS | Public HF dataset | Usable code and pretrained predictors | No-reference MOS baseline | Generated-system MOS may not transfer to amateur coaching |
| [SingMOS-v1](https://arxiv.org/abs/2406.10911), [dataset](https://huggingface.co/datasets/TangRain/SingMOS-v1) | 3,421 singing clips, 4.25h, Chinese/Japanese MOS | Public HF dataset, license metadata inconsistent across pages | Usable through SingMOS repo | Smaller MOS baseline | Dataset viewer issues and license ambiguity should be checked before release use |
| [GTSinger](https://arxiv.org/abs/2409.13832), [code](https://github.com/AaronZ345/GTSinger), [dataset](https://huggingface.co/datasets/AaronZ345/GTSinger) | 80.59h, 20 professional singers, 9 languages, technique labels and alignments | Public metadata, data release under license | Usable code | Technique recognition and controlled vocal-style probes | Professionals only, not overall amateur quality |
| [Lyra-SA](https://lyracobar.y.qq.com/singvoicedataset_en.html) | 1,000 mobile-karaoke songs, 100 singers, 10 songs, MIDI/lyrics, ordinary-listener singing ratings, timbre gender/age | Application, CC BY-NC 4.0 | Code not verified | Real-user karaoke assessment with reference information | Labels are rough listener judgments; phone/accompaniment leakage possible |
| [SVQTD](https://yanzexu.xyz/SVQTD/), [paper](https://link.springer.com/article/10.1186/s13636-022-00240-z) | Nearly 4,000 tenor segments, 10.7h, 7 pedagogy labels: resonance, placement, openness, roughness, vibrato | Signed agreement and email | No verified runnable model code | Pedagogical attribute recognition | Classical tenor domain; source separation artifacts; request-based data |
| [VocalSet](https://archives.ismir.net/ismir2018/paper/000114.pdf), [Zenodo](https://zenodo.org/records/10200775) | 10.1h a cappella, 20 professionals, 17 techniques, vowels/contexts | Public Zenodo | Data usable; simple baselines reproducible | Low-cost technique classifier | Not a skill-quality dataset |
| [PESnQ](https://github.com/chitralekha18/PESnQ_APSIPA2017), [SingEval](https://github.com/chitralekha18/SingEval), [APSIPA 2021 explainable SQA](https://www.apsipa.org/proceedings/2021/pdfs/0000904.pdf) | Reference-dependent short clips, DAMP/Smule quality annotations, BWS/pairwise labels, pitch/rhythm labels in related work | Code public; raw audio/annotations have access friction | Usable with access work | Explainable pitch/rhythm/overall baselines | DAMP audio not bundled; Praat/reference-song assumptions |
| [TG-Critic](https://arxiv.org/abs/2305.09127), [repo](https://github.com/YuejieGao/TG-CRITIC) | NUS48E/PESnQ-DS labels and results, three quality classes | Public repo | Partial labels/results, no full runnable stack verified | Related no-reference scoring reference | Survey/reference unless implementation is obtained or recreated |
| [VocalVerse / QwenFeat-Vocal-Score](https://github.com/CarlWangChina/QwenFeat-Vocal-Score), [model](https://huggingface.co/karl-wang/QwenFeat-Vocal-Score), [dataset](https://huggingface.co/datasets/karl-wang/VocalVerse-dataset/) | About 1,000 open high-proficiency KTV clips from a larger pool, amateur MOS, professional timbre/breath/emotion/technique scores and critiques | Public, ungated HF model and dataset; non-commercial/no-derivatives license | Usable but heavy | Modern multi-dimensional critique; possible data source | QwenAudio path is large; top-10-percent filtering biases range |
| 10KSinging / ICME 2023 / ISMIR 2024 | 9,756 songs, singer ratings from Bilibili leaderboard videos, solo/accompaniment variants | Proprietary | No open benchmark gate | Survey/reference | Single-annotator/reputation bias and no public data/code |
| Learn by Referencing / ranking papers | Pair/triplet and pairwise preference methods, internal WeSing-like data | Mostly not public | Survey/reference | Experiment-design pattern | Useful for label design, not a direct baseline |
| MFFMOS / GOSMOS | Hokkien Gezi Opera MOS and reference-free MOS feature fusion | Full source extraction blocked by ScienceDirect 429 | Survey/reference | Current MOS trend evidence | No verified code/data |
| Nakano/MiruSinger | Pitch interval and vibrato cues, real-time feedback system | Historical papers/pages | Survey/reference | Interpretable feedback design | Not a modern benchmark |

## Metrics to Use

### Regression and MOS

- MSE and MAE for absolute score error.
- Pearson/LCC for linear agreement.
- Spearman/SRCC and Kendall tau for rank agreement.
- Calibration curves and expected calibration error if scores are presented to
  users.
- Bootstrap confidence intervals over singers and songs, not only over clips.

### Classification and Attributes

- Macro-F1 and UAR for imbalanced technique or pedagogy labels.
- Balanced accuracy and class-wise recall.
- Confusion matrices for near-neighbor labels.
- Ordinal metrics for ordered labels such as resonance or openness classes.

### Ranking and Preference

- Pairwise accuracy.
- Spearman/Kendall rank correlation.
- Best-worst scaling score correlation.
- Human inter-rater agreement as a ceiling.

### Feedback Quality

- Dimension-wise correlation for pitch, rhythm, timbre, breath, emotion, and
  technique.
- Error localization precision: whether the marked section is the true weak
  section.
- Human preference for feedback usefulness, separated from score accuracy.

## Splits and Leakage Controls

Minimum controls:

- singer-disjoint split for all models intended to generalize;
- song-disjoint or at least song-stratified evaluation for karaoke scoring;
- system-disjoint split for SingMOS-Pro generated-system MOS;
- no same recording or derived segment in both train and test;
- no same singer through filename, uploader, accompaniment, or separation
  artifact leakage;
- per-language and per-gender reporting where labels permit;
- report results with and without accompaniment/source separation.

For the current larger project on leakage and disentanglement, these controls are
especially important. Singing evaluators can accidentally learn identity,
recording chain, source-separation artifacts, song difficulty, or dataset origin
instead of singing quality.

## Karaoke Score Traps

1. Reference matching is not musical quality. A score-following system can punish
   good phrasing, ornamentation, intentional timing, transposition, and expressive
   vibrato.
2. Accompaniment leakage is common in real mobile recordings. A model can learn
   backing-track mix quality or source-separation artifacts.
3. Pitch accuracy is not enough. Timbre, breath, register transitions,
   resonance, diction, expression, and style all matter.
4. Popularity is not skill. Leaderboards and platform ratings can encode
   reputation, song choice, mixing, genre preference, and audience demographics.
5. Single-annotator labels are fragile. 10KSinging-style labels are useful for
   weak supervision but not for teacher-grade claims.
6. Generated-vocal MOS is not human coaching. SingMOS-Pro is strong for
   perceived naturalness/quality, but the distribution includes SVS systems, not
   only real amateur singers.
7. Segment-level scores can erase phrase-level context. Breath control and
   expression often need longer windows.
8. Future professional potential is not observable in the available datasets.
   Do not infer future outcomes from current MOS without a longitudinal study.

## Baseline Recommendations

### Use First

- **SingMOS-Pro/SingMOS**: no-reference MOS predictor and frozen-embedding
  regression baseline.
- **GTSinger**: technique recognition baseline with singer-disjoint splits.
- **VocalSet**: lightweight technique classifier and embedding sanity check.
- **PESnQ/SingEval/AME430**: reference-conditioned and explainable scoring, if
  DAMP/annotation access is solved.

### Use With Compute/License Caution

- **VocalVerse/QwenFeat-Vocal-Score**: excellent modern label schema and open
  assets, but the QwenAudio route is heavy and the license is non-commercial and
  no-derivatives. Prefer the dataset and MuQ/SongEval-style branch for a smaller
  research baseline.

### Reference Only By Default

- **TG-Critic**: labels/results are useful, but full runnable code was not
  verified.
- **10KSinging / ICME 2023 / ISMIR 2024**: proprietary data/code, useful as
  framing.
- **Learn by Referencing / twin network / leaderboard papers**: important label
  and ranking-design patterns, but not turnkey benchmarks.
- **MFFMOS/GOSMOS**: current MOS direction, but source extraction/code/data were
  not verified.
- **Nakano/MiruSinger**: historical feedback design.

## Three Small-GPU Experiment Designs

### Experiment 1: Technique and Attribute Probe

Goal: verify whether frozen audio embeddings can identify singing technique and
pedagogy-relevant attributes on open or requestable datasets.

Data:

- VocalSet for public technique labels.
- GTSinger for mixed voice, falsetto, breathy, pharyngeal, vibrato, and
  glissando.
- Optional SVQTD if data access is approved.

Model:

- Precompute frozen embeddings with wav2vec2/HuBERT/WavLM/BEATs/MuQ.
- Train a small MLP, logistic regression, or shallow temporal pooling head.
- Add explicit F0, vibrato-rate/depth, energy, and spectral tilt features as
  interpretable auxiliaries.

Splits and metrics:

- Singer-disjoint splits.
- Macro-F1, UAR, class-wise recall, confusion matrices.
- Ablate learned embedding only, handcrafted features only, and fused features.

Small-GPU feasibility:

- Precompute embeddings once; train heads on a single 8-12 GB GPU or CPU.

Why it matters:

- Establishes whether the project can produce reliable component feedback before
  attempting global skill claims.

### Experiment 2: No-Reference Quality Baseline With Calibration

Goal: build a current-quality baseline that is honest about uncertainty and
dataset distribution.

Data:

- SingMOS-Pro as the primary MOS dataset.
- SingMOS-v1 as a smaller check.
- Optional VocalVerse MOS/professional dimensions for transfer, respecting the
  license.
- Optional SingEval if audio and annotations are obtained.

Model:

- Compare the released SingMOS predictor with frozen SSL embeddings plus ridge,
  random forest, and small MLP heads.
- Add simple F0 stability, voicing, energy, and vibrato statistics.
- Train both utterance-level and pooled system/singer-level variants where labels
  support it.

Splits and metrics:

- System-disjoint and dataset-disjoint splits for SingMOS-Pro.
- If real-user data is added, use singer-disjoint and song-disjoint splits.
- MSE, MAE, Pearson/LCC, Spearman/SRCC, Kendall tau, and calibration curves.
- Report judge-variance-aware uncertainty when individual judge scores exist.

Small-GPU feasibility:

- Frozen embeddings plus shallow heads are cheap. The released SingMOS predictor
  can serve as a direct baseline.

Why it matters:

- Provides a reproducible "current perceived quality" baseline while avoiding
  unsupported future-potential claims.

### Experiment 3: Pairwise Improvement and Actionable Feedback

Goal: avoid absolute-score brittleness by learning which take is better and why.

Data:

- Lyra-SA if access is approved, using MIDI/lyrics and song splits.
- PESnQ/SingEval/AME430 data if audio access is solved.
- A small self-collected pilot: 20-50 singers, two or three takes of the same
  song section before/after simple feedback, pairwise labels from trained
  listeners.

Model:

- Extract pitch/rhythm alignment to MIDI or reference with `torchcrepe`, `crepe`,
  `librosa`, or similar tools.
- Add timbre/technique embeddings from Experiment 1.
- Train a pairwise logistic/RankNet/LambdaRank head over take pairs.
- Output top contributing weak dimensions rather than only a score.

Splits and metrics:

- Singer-disjoint validation for generalization.
- Pairwise accuracy, Spearman/Kendall over take rankings, and human agreement
  ceiling.
- Ablate reference alignment, technique features, and learned audio embeddings.

Small-GPU feasibility:

- Mostly feature extraction and shallow ranking models; a single consumer GPU is
  enough after embedding precomputation.

Why it matters:

- This is the closest small study to "improvement potential" without claiming to
  predict professional futures.

## Recommended Research Shape

The safest paper/product claim is:

> A source-controlled singing assessment benchmark that combines no-reference
> perceived quality, reference-conditioned pitch/rhythm diagnostics, and
> technique/attribute probes, with explicit leakage controls and uncertainty.

Do not start with a single "future professional" classifier. Start with current
quality and interpretable dimensions. Add longitudinal potential only after
collecting repeated recordings and future outcomes.

For the active leakage/disentanglement project, the singing-skill survey points to
an interesting bridge: many assessment labels are entangled with singer identity,
song, recording path, and source separation. Any singing-skill evaluator should
therefore include leakage probes for singer, song, accompaniment, and dataset
origin alongside quality metrics.

## Source Evidence Store

Detailed extraction notes were written under:

- `survey/papers/singing-skill-singmos-pro/`
- `survey/papers/singing-skill-gtsinger/`
- `survey/papers/singing-skill-lyra-sa/`
- `survey/papers/singing-skill-svqtd/`
- `survey/papers/singing-skill-vocalset/`
- `survey/papers/singing-skill-pesnq-singeval/`
- `survey/papers/singing-skill-tg-critic/`
- `survey/papers/singing-skill-rank-and-reference/`
- `survey/papers/singing-skill-singmd-vocalverse/`
- `survey/papers/singing-skill-mffmos-gosmos/`
- `survey/papers/singing-skill-nakano-mirusinger/`
