# TG-Critic

## Idea

TG-Critic is a reference-independent singing evaluation method that uses timbre
embeddings and a multi-scale CQT trunk. It targets broad perceived quality rather
than reference-note correctness.

## Method

The paper describes automatic annotation for three-class singing quality and a
model that combines timbre information with CQT-based acoustic features.

## Datasets and Labels

The public repository contains subjective overall-score ground truth for NUS48E
and PESnQ-DS plus results for TG-Critic and comparison algorithms. Labels are
three classes: excellent, mediocre, and inferior, with descriptions tied to
intonation, representation, and voice quality.

## Metrics and Experiments

Reported metrics in the repository include accuracy, Pearson correlation, and
macro AUC on YJ-900, PESnQ-DS, and NUS48E.

## Ablations

The repository includes ablation tables for TG-Critic variants, including
two-stage variants and metric comparisons.

## Code Availability

Partial. `git ls-remote https://github.com/YuejieGao/TG-CRITIC` succeeded, but
the repository appears to publish labels/results rather than a complete runnable
training/inference stack. Treat as survey/reference by default.

## Relevance

Useful for framing no-reference scoring and label rubrics. Not a benchmark gate
unless the missing implementation is re-created or obtained.
