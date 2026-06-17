# NaturalSpeech 3 / FACodec (2024)

## Idea

Speech generation improves when the waveform is factorized into attribute
subspaces: content, prosody, timbre, and acoustic details.

## Method

FACodec uses factorized vector quantization and explicit disentanglement losses,
including phone/F0 prediction losses and gradient-reversal losses for phone,
F0, and speaker classification. NaturalSpeech 3 then models the factorized
attributes with diffusion components.

## Experiment Design

The paper evaluates zero-shot TTS and the codec separately. FACodec is tested on
reconstruction and zero-shot VC by swapping speaker embedding while retaining
source content/prosody/detail codes.

## Datasets and Metrics

Training/evaluation sources include LibriLight, LibriSpeech test-clean, VCTK,
and RAVDESS. Reported metrics include Sim-O/Sim-R, WER, UTMOS, CMOS/SMOS for
TTS; PESQ, STOI, MSTFT, and MCD for codec reconstruction; and Sim-O/WER for VC.

## Ablations

Reported ablations include duration diffusion design, information bottleneck for
codec disentanglement, gradient reversal, and acoustic-detail quantizers.

## Code Availability

Usable public FACodec code and pretrained weights are available. This is a real
benchmark candidate for frozen stream leakage probes and for factorized-codec
comparison. It is speech-trained and not guaranteed to reconstruct singing well.

## Relevance

FACodec is the strongest immediately reusable factorized-codec baseline. Any
claim that the project newly separates content/prosody/timbre/residual must be
narrowed to speech-versus-singing mode residuals, unseen singer evaluation, and
downstream Seed-VC conditioning.

Sources: https://arxiv.org/abs/2403.03100,
https://github.com/lifeiteng/naturalspeech3_facodec,
https://github.com/Plachtaa/FAcodec

