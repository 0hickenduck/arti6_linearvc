# MSR-Codec (2025)

## Idea

A low-bitrate multi-stream residual codec can represent semantic, timbre,
prosody, and residual streams while preserving high-fidelity reconstruction and
supporting independent manipulation.

## Method

The codec encodes speech into semantic, timbre, prosody, and residual streams
and uses the stream structure for speech generation and voice conversion.

## Experiment Design

The paper evaluates codec reconstruction, TTS, and voice conversion, including
speaker-similarity and intelligibility measures.

## Datasets and Metrics

The abstract highlights WER and speaker similarity for downstream TTS/VC in
addition to codec reconstruction quality. Full metric extraction should be
completed before implementation if MSR-Codec becomes a baseline.

## Ablations

The paper's relevant ablation pattern is stream-level manipulation and residual
factorization. Full ablation details should be extracted from the PDF before
benchmarking.

## Code Availability

The arXiv page says inference code, pretrained models, and samples are public.
The GitHub repository contains source, checkpoints, `inference.py`, and
`infer.sh`. This makes it a possible baseline, but the current task did not
clone or run it; benchmark status is conditional on local install and checkpoint
verification.

## Relevance

MSR-Codec weakens any claim that residual streams or multi-stream
factorization are novel. It may strengthen the project as a baseline if its
streams can be probed on GTSinger under the same split.

Sources: https://arxiv.org/abs/2509.13068,
https://github.com/herbertLJY/MSRCodec

