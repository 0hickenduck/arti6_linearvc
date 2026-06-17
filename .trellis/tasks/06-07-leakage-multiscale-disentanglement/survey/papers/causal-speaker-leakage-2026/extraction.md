# Causally Disentangled Contrastive Learning for Multilingual Speaker Embeddings (2026)

## Idea

Speaker embeddings can encode demographic attributes. Leakage can be measured
with linear and nonlinear probes, but debiasing creates verification tradeoffs.

## Method

The paper studies SimCLR-trained speaker embeddings with adversarial
gradient-reversal debiasing and a causal bottleneck architecture that separates
demographic and residual information.

## Experiment Design

Demographic leakage is quantified with both linear and nonlinear probing
classifiers. Speaker verification is evaluated with ROC-AUC and EER.

## Datasets and Metrics

The abstract describes gender, age, and accent leakage in multilingual speaker
embeddings. Metrics include probe performance, ROC-AUC, and EER.

## Ablations

The core ablations compare baseline embeddings, adversarial debiasing, and
causal bottleneck tradeoffs; gender leakage is reported as strongly linearly
encoded, while age/accent are weaker and more nonlinear.

## Code Availability

No usable public code was found in targeted search. Survey/reference only.

## Relevance

This sets the methodological bar: use both linear and nonlinear probes and
report the leakage/verification Pareto curve. It also warns that stronger
disentanglement may damage speaker verification.

Source: https://arxiv.org/abs/2602.01363

