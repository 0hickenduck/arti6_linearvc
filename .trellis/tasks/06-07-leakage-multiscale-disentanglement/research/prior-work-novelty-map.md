# Prior-Work and Novelty Map

Research cutoff: 2026-06-07.

## Question

Has prior work already combined all of the following?

1. Mean/std or residual decomposition of frame-level speech representations.
2. Multiple temporal scales.
3. Explicit leakage probes for speaker, vocal mode, content, and prosody.
4. Speech-versus-singing evaluation on held-out speakers.
5. A downstream test showing that selective recombination closes the
   cross-mode identity gap without damaging content or melody.

## Closest Work

| Work | Relevant contribution | Overlap | Remaining gap for this project | Public implementation found |
| --- | --- | --- | --- | --- |
| AdaIN-VC (Interspeech 2019) | Uses instance normalization to separate content from speaker-related channel statistics. | Global mean/std normalization. | No speech/singing study, multiscale leakage map, or stable-core versus mode-residual analysis. | Paper and third-party implementations exist; not selected as the primary implementation base. |
| LoIN (Interspeech 2023) | Uses local feature statistics and consistency constraints to improve VC decoupling. | Local rather than only global statistics. | Does not map leakage across explicit temporal bands or study vocal-mode-conditioned identity. | No maintained official implementation identified in the targeted search. |
| FACodec / NaturalSpeech 3 (2024) | Factorizes content, prosody, timbre, and residual acoustic detail. | Explicit factor streams and residual branch. | Primarily TTS/codec evaluation; not a crossed speech/singing leakage study. | Yes: `lifeiteng/naturalspeech3_facodec`, pretrained weights available. |
| FreeCodec (2024) | Global timbre vector, long-stride prosody encoder, and content encoder. | Different temporal resolutions for different factors. | Does not test our stable identity versus speaker-specific vocal-mode residual hypothesis. | Paper found; no official reusable implementation identified in the targeted search. |
| MERL disentangled codec (arXiv 2025, ICASSPW 2026) | Quantized SSL content, residual-derived speaker mean/std, and normalized residual prosody. | Very close to the proposed global residual plus statistics baseline. | English speech only; limited factor leakage tests; no singing, multiscale statistics, or unseen-speaker identity-gap correction. | No public code identified in the targeted search. |
| MSR-Codec (2025) | Multi-stream residual codec with semantic, timbre, prosody, and residual streams. | Residual factorization and independent stream manipulation. | No controlled speech/singing leakage map or condition-specific speaker residual study. | No public code identified in the targeted search. |
| InterpTRQE-SptME (2025) | Measures residual speaker information in SSL content embeddings and proposes filtering. | Direct speaker-leakage audit of pretrained speech representations. | Speaker/content focus rather than vocal mode, temporal bands, and downstream singing conversion. | No implementation selected yet; paper claims a model-agnostic filtering benchmark. |
| Privacy-preserving Prosody Representation Learning (2026) | Learns prosody representations while suppressing speaker identity; evaluates prosody tasks and speaker disentanglement. | Speaker leakage from prosody representations and utility/leakage tradeoff. | Does not study speech/singing identity residuals or multiscale selective recombination. | No public code identified in the targeted search. |
| Causally Disentangled Contrastive Learning for Multilingual Speaker Embeddings (2026) | Uses linear/MLP probes, adversarial debiasing, and a causal bottleneck for demographic leakage. | Strong precedent for probe methodology and utility/leakage Pareto curves. | Attributes are gender, age, and accent rather than vocal mode/content/prosody; no synthesis intervention. | No public code identified in the targeted search. |

## Judgment

The individual ingredients are not novel:

- global or local mean/std normalization;
- residual streams;
- content/prosody/timbre factorization;
- linear and nonlinear leakage probes;
- adversarial removal of nuisance attributes;
- the observation that speech and singing produce different speaker embeddings.

The potentially defensible combination is:

> A controlled map of where speaker, vocal mode, content, and prosody information
> occur across SSL layers and temporal-statistical bands, followed by a
> stable-speaker-core plus speaker-specific vocal-mode-residual factorization,
> evaluated on unseen singers and connected to speech-reference singing voice
> conversion.

The contribution must include the downstream result. A probe-only paper would
overlap heavily with recent leakage audits. A new codec trained from scratch is
not justified until the frozen-representation audit establishes a useful
factorization.

## Important Dataset Boundary

GTSinger contains 20 singers across nine languages with paired speech and
singing, but each singer is associated with one language. It supports a
speech-versus-singing study. It does **not** independently identify language
leakage in speaker representations, because language and speaker identity are
confounded.

A language claim requires the same speakers recorded in multiple languages.
The VTuber corpus could eventually support an EN/JP case study, but only after
speaker, language, channel, accompaniment, and vocal-mode labels are controlled.

## Sources

- [AdaIN-VC](https://www.isca-archive.org/interspeech_2019/chou19_interspeech.html)
- [LoIN](https://www.isca-archive.org/interspeech_2023/gu23b_interspeech.html)
- [NaturalSpeech 3 / FACodec](https://arxiv.org/abs/2403.03100)
- [FACodec implementation](https://github.com/lifeiteng/naturalspeech3_facodec)
- [FreeCodec](https://arxiv.org/abs/2412.01053)
- [MERL disentangled codec](https://arxiv.org/abs/2508.08399)
- [MERL ICASSPW paper](https://www.merl.com/publications/docs/TR2026-035.pdf)
- [MSR-Codec](https://arxiv.org/abs/2509.13068)
- [Speaker Disentanglement of Speech Pre-trained Model Based on Interpretability](https://arxiv.org/abs/2507.17851)
- [Privacy-preserving Prosody Representation Learning](https://arxiv.org/abs/2606.00407)
- [Causally Disentangled Contrastive Learning for Multilingual Speaker Embeddings](https://arxiv.org/abs/2602.01363)
- [GTSinger](https://proceedings.neurips.cc/paper_files/paper/2024/hash/023d2c1a17cf35b11a0cbb43a0677c91-Abstract-Datasets_and_Benchmarks_Track.html)

