# SingMOS / SingMOS-Pro

## Idea

SingMOS builds a mean-opinion-score benchmark and predictors for perceived singing
voice quality. SingMOS-Pro extends the setup to a larger multi-system evaluation
dataset for singing voice synthesis outputs and real vocals.

## Method

The public code exposes ready-to-use MOS predictors through `torch.hub`, including
`singmos_v1` and `singmos_pro` model specifiers. The reported predictor family
uses wav2vec-style speech representations followed by a MOS regression head.

## Datasets and Labels

- SingMOS-v1: 3,421 clips, 4.25 hours, Chinese and Japanese, 16 kHz, with
  utterance-level MOS metadata.
- SingMOS-Pro: 7,981 clips, 11.15 hours, Chinese and Japanese vocals from 41
  generated systems across 12 datasets. Each clip was rated by at least five
  experienced annotators. The Hugging Face repository includes `split.json`,
  `score.json`, `sys_info.json`, and `metadata.csv`.

## Metrics and Experiments

Primary metrics are MOS prediction/regression metrics, with utterance and system
MOS. Useful local evaluation should report MSE/MAE, Pearson/LCC, Spearman/SRCC,
Kendall tau, and calibration by dataset/system.

## Ablations

Use as an anchor for ablations rather than as the full study: frozen SSL
embedding plus linear/ridge/MLP head, F0 and energy feature additions, singer- or
system-disjoint splits, and zero-shot transfer to real-user singing sets.

## Code Availability

Usable. `git ls-remote https://github.com/South-Twilight/SingMOS` succeeded, and
the README documents `torch.hub` inference for pretrained MOS predictors. Guessed
Hugging Face model API paths under `TangRain/*` were inaccessible, recorded in
`evolution.md`, but the GitHub route is sufficient for the benchmark gate.

## Relevance

Best open code/data candidate for a no-reference perceived-quality baseline.
It does not answer "future professional potential" and is partly biased toward
generated-system MOS rather than human coaching outcomes.
