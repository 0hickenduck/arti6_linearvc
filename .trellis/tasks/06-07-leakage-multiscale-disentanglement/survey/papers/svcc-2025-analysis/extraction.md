# SVCC 2025 Analysis

## Idea

Singing conversion has moved beyond singer identity conversion toward singing
style conversion, where naturalness and style dynamics remain difficult even
when identity similarity improves.

## Method/Benchmark

SVCC 2025 defines in-domain and zero-shot singing style conversion tasks with
source singing, target/reference style constraints, waveform data, aligned
phoneme/MIDI, global/local style labels, and transcriptions.

## Experiment Design

The analysis reports a controlled challenge with 33 systems, large-scale
crowd-sourced listening tests, and objective evaluations.

## Datasets and Metrics

Subjective scores cover singer identity, style similarity, dynamic preference,
and naturalness. Objective metrics include chroma-alignment and speaker
embedding/non-match metrics; the paper reports these correlate with subjective
scores but do not replace listening tests.

## Ablations

The challenge itself provides system comparisons rather than one model's
internal ablations. It is useful as an evaluation pattern.

## Code Availability

The challenge page states baseline code and a technical paper were released, but
training data was sent to registered participants. Treat as an evaluation
reference, not a drop-in benchmark unless data and baseline scripts are obtained.

## Relevance

This is a reviewer-facing reminder that objective speaker metrics are not enough
for singing conversion claims. Stage C must include blinded listening once it
makes synthesis claims.

Sources: https://arxiv.org/abs/2509.15629,
https://vc-challenge.org/

