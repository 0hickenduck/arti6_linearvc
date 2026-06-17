# FreeCodec (2025)

## Idea

A neural speech codec can use fewer tokens by explicitly separating global
timbre, low-rate prosody, and content.

## Method

FreeCodec uses a pretrained ECAPA-TDNN speaker encoder for global timbre, a
content encoder trained with WavLM-large targets, and a long-stride prosody
encoder whose output is about 7 Hz. It trains variants for reconstruction and
voice conversion/disentanglement scenarios.

## Experiment Design

Experiments test reconstruction quality on VCTK and LibriSpeech test-clean and
disentanglement through a LibriSpeech-to-VCTK voice conversion benchmark.

## Datasets and Metrics

Training uses LibriSpeech train-clean-100, train-clean-360, and train-other-500.
Reconstruction metrics include UTMOS, STOI, WARP-Q, and speaker embedding
cosine similarity. VC metrics include WER, CER, F0 Pearson correlation, and
SECS.

## Ablations

Reported ablations include content loss removal and variant comparisons across
FreeCodec-v1/v2/v3.

## Code Availability

The arXiv page points to a GitHub repository, but the repository README still
states that paper, code, and pretrained model will be released soon and only a
demo is visible. Classify as survey/reference only until usable inference code
and checkpoints are available.

## Relevance

FreeCodec is a citation-chain risk for temporal-factor claims because it already
uses a global timbre vector, 50 Hz content, and roughly 7 Hz prosody. It is not a
benchmark gate today without usable code.

Sources: https://arxiv.org/abs/2412.01053,
https://github.com/exercise-book-yq/FreeCodec

