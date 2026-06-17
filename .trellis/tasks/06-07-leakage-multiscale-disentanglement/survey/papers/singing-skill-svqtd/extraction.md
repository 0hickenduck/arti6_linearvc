# SVQTD

## Idea

SVQTD frames singing quality as vocal-pedagogy attribute recognition for classical
tenor singing. It provides labels closer to coaching concepts than a single
karaoke score.

## Method

YouTube tenor performances were source-separated with Spleeter, voice-activity
segmented, then annotated by trained annotators under supervision. Baselines in
the paper include openSMILE feature SVMs, end-to-end deep learning, and deep
embedding plus SVM models.

## Datasets and Labels

Nearly 4,000 vocal solo segments, 4-20 seconds each, about 10.7 hours, from 400
audios of six famous tenor arias. Seven labels: chest resonance, head resonance,
front placement, back placement, openness/open throat, roughness, and vibrato
quality. Annotators had at least three years of classical training and underwent
additional training.

## Metrics and Experiments

The paper reports unweighted average recall (UAR) for class-imbalanced ordinal
and binary labels. Local experiments should use UAR, macro-F1, ordinal error for
ordinal scales, and leave-singer/video/aria-out splits when possible.

## Ablations

Important ablations: handcrafted acoustic features versus SSL embeddings, effect
of source separation artifacts, label-by-label performance, and cross-aria
generalization.

## Code Availability

Dataset access is by signed agreement and email. The public `hackerpeter1/SVQTD`
repository is a landing-page/audio-example site, not verified model code. Guessed
author GitHub repositories returned "Repository not found" and were recorded in
`evolution.md`.

## Relevance

Excellent reference for pedagogical rubrics and attribute labels. Not a turnkey
benchmark unless dataset access is approved and baselines are reimplemented.
