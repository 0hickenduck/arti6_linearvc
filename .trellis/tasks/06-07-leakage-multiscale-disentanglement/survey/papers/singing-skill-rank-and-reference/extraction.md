# Ranking and Reference-Based Singing Skill Work

## Idea

These papers avoid brittle absolute labels by learning relative quality:
reference-conditioned triplet/ranking losses, pairwise preference networks, and
leaderboard reconstruction from relative singer statistics.

## Method

"Learn by Referencing" constructs clip pairs/triplets with weak labels and trains
metric-learning models against reference singers. The ISMIR 2020 twin-network
paper uses pairwise comparisons to learn which singer is better, optionally
conditioned on pitch histograms. The leaderboard work combines absolute pitch
histograms and inter-singer relative statistics through truth-finding.

## Datasets and Labels

The WeSing/leaderboard sources are not fully open. The ISMIR 2021 paper reports
15,487 three-second clip pairs from 1,240 full recordings over 102 songs, plus a
test set of 45 recordings judged by five professionals.

## Metrics and Experiments

Common metrics are Pearson, Spearman, pairwise accuracy, and agreement with human
rankings. The twin-network paper reports pairwise accuracy and correlation on
unseen songs; the leaderboard work reports Spearman correlation close to
inter-judge agreement.

## Ablations

Relevant ablations: same-song versus cross-song comparisons, number of pairwise
comparisons, pitch-histogram conditioning, reference quality, and weak-label
thresholds.

## Code Availability

No verified usable public code/data for local benchmarking. Treat as
survey/reference.

## Relevance

Important design pattern for small human-label budgets: ask humans which take is
better instead of asking for stable absolute "potential" scores.
