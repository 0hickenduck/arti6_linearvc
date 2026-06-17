# AdaIN-VC (2019)

## Idea

Instance normalization can remove channel-wise utterance statistics from speech
features and thereby support a content/speaker separation for one-shot voice
conversion.

## Method

The model uses instance normalization as an inductive bias for content
representation and adaptive/target conditioning to recover speaker traits from a
reference utterance.

## Experiment Design

The paper evaluates one-shot VC with unseen speakers using objective and
subjective similarity/quality tests. It is a generative VC study, not a
speech-versus-singing or leakage-probing study.

## Datasets and Metrics

Reported as one-shot VC experiments. The key reported evidence is target-speaker
similarity and subjective conversion quality.

## Ablations

The relevant ablation pattern is the use of normalization to remove
speaker-related statistics. It does not test local/multiscale statistics,
phonetic controls, F0 controls, or downstream singing conversion.

## Code Availability

No maintained official implementation was selected as a benchmark gate. Treat as
survey/reference only unless the user explicitly accepts third-party
implementation risk.

## Relevance

This is the citation-chain risk for any claim that mean/std normalization of
frame-level speech representations is new. The current project must cite it and
make clear that the novelty is not global statistics, but a controlled
speech/singing identity-residual experiment.

Sources: https://arxiv.org/abs/1904.05742,
https://www.isca-archive.org/interspeech_2019/chou19_interspeech.html

