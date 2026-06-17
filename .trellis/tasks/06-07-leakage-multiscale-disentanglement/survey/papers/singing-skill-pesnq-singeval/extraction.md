# PESnQ / SingEval / Explainable SQA

## Idea

This line of work treats singing quality as a combination of reference-dependent
pitch/rhythm correctness, expert or crowd quality scores, and explainable
component feedback.

## Method

PESnQ extracts perceptual singing-quality features from a test singing clip and a
reference of the same song, then exports features for WEKA-style models. The 2021
explainable SQA work uses multitask CRNN-style models and augmented negative
samples to predict overall quality and pitch/rhythm components.

## Datasets and Labels

- PESnQ: short monophonic 16 kHz clips with expert ground truth and matched
  reference singing for songs such as "Edelweiss" and "I Have a Dream".
- SingEval: human-annotated singing-quality scores for a subset of Smule DAMP
  vocals; the repository provides annotations and metadata, not raw audio.
- APSIPA 2021 DAMP subset: 4 popular English songs, 100 performers per song, five
  20-30 second segments, mixed skill levels, crowd pairwise/BWS annotations.
- Additional cited datasets include Databaker Mandarin and NHSS, with access
  constraints.

## Metrics and Experiments

Reported metrics include Pearson correlation for overall score, pitch-score
correlation, and pitch-classification accuracy. Local experiments should also use
Spearman/Kendall for ranking and per-song splits.

## Ablations

Useful ablations: reference-dependent pitch/rhythm features versus no-reference
embeddings, augmented negative samples, multitask versus single-task heads,
component-specific heads, and song-disjoint evaluation.

## Code Availability

Usable but not frictionless. `PESnQ_APSIPA2017`, `SingEval`, and both AME430
repositories were reachable via `git ls-remote`. PESnQ needs Praat, same-song
reference singing, and short clips. SingEval does not include DAMP audio, so
audio access must be solved separately.

## Relevance

One of the strongest practical paths for explainable feedback, provided the
project accepts dataset-access work and reference-conditioned assumptions.
