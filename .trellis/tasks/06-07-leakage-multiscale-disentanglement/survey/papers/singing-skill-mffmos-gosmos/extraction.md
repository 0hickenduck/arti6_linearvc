# MFFMOS / GOSMOS

## Idea

MFFMOS is a reference-free singing voice MOS prediction approach with multi-feature
fusion and integrated feature analysis. GOSMOS is described as a public Hokkien
Gezi Opera MOS dataset.

## Method

The available metadata describes feature fusion over initial perception,
pronunciation clarity, timbre, pitch, and emotion, plus integrated analysis for
reference-based feedback.

## Datasets and Labels

GOSMOS reportedly contains professional singer material plus SVS and manipulated
low-quality audio rated by six professionals. Lyra-SA is also used as a public
Chinese singing dataset in the study.

## Metrics and Experiments

Reported metric family: MSE, LCC/Pearson, SRCC/Spearman, and Kendall tau.

## Ablations

The paper title and metadata imply feature-fusion ablations and feature-analysis
studies, but full details were not extracted because the ScienceDirect page was
rate limited.

## Code Availability

No verified usable code/data during this run. ScienceDirect returned HTTP 429 and
the problem was recorded in `evolution.md`. Treat as survey/reference.

## Relevance

Useful as evidence that current singing-MOS research is moving toward
interpretable dimensions, but not a benchmark gate.
