# Lyra-SA

## Idea

Lyra-SA is a real mobile-karaoke singing assessment dataset from WeSing-like
recordings. It is one of the few public-facing sources with ordinary-user
performances, reference MIDI/lyrics, and human assessment labels.

## Method

The data supports reference-conditioned evaluation: compare a user performance to
song structure, MIDI/lyrics, and potentially a high-quality reference. The related
ISMIR 2021 "Learn by Referencing" work uses metric learning over clip pairs and
expert test-set ratings.

## Datasets and Labels

The source page describes 100 singing voices and MIDI/lyrics for 10 songs, one
sample per singer, yielding 1,000 complete songs. Recordings were captured through
iOS/Android phone microphones in real mobile karaoke environments, resampled to
44.1 kHz mono 16-bit. Ordinary listeners rated singing and marked timbre gender
and age. Suggested song split: songs 1-6 train, 7-8 validation, 9-10 test.

## Metrics and Experiments

Use Pearson/Spearman for scalar labels, pairwise accuracy if converting labels to
preferences, and pitch/rhythm alignment metrics against MIDI. Always report per
song and cross-song results because song difficulty and key are major confounds.

## Ablations

Useful ablations: reference-conditioned versus no-reference models, pitch/rhythm
features versus learned audio embeddings, phone-mic/noise handling, accompaniment
leakage handling, and song-disjoint splits.

## Code Availability

Dataset is available by application under CC BY-NC 4.0. Code for the dataset
itself was not verified. The related Learn by Referencing paper is useful as a
method pattern but used internal WeSing data and large-GPU training.

## Relevance

High-value real-user dataset for a karaoke-style task, but labels are rough
ordinary-listener judgments rather than teacher-grade diagnostic labels.
