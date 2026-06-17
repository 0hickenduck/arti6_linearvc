# Privacy-preserving Prosody Representation Learning (2026)

## Idea

Prosody representations are useful but leak speaker identity because acoustic
prosody includes pitch and other speaker-correlated cues.

## Method

The paper proposes a self-supervised prosody encoder with speaker
disentanglement strategies to improve the prosody utility/privacy tradeoff.

## Experiment Design

The encoder is evaluated on prosody tasks including pitch reconstruction and
prosodic event detection, while assessing speaker disentanglement against raw
prosody and HuBERT-base baselines.

## Datasets and Metrics

The abstract reports pitch reconstruction, prosodic event detection, and speaker
disentanglement. Full dataset/metric extraction should be completed if this work
becomes more central.

## Ablations

The relevant pattern is utility/leakage tradeoff evaluation for prosody
representations.

## Code Availability

No usable public code was found in targeted search. Survey/reference only.

## Relevance

This is a timely citation-chain risk for any claim that speaker leakage in
prosody is new. It also supports the project's need to control F0 and prosody
before interpreting mode residuals.

Source: https://arxiv.org/abs/2606.00407

