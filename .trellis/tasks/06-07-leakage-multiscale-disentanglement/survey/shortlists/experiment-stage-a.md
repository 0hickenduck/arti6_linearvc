# Stage A Experiment Shortlist

Date: 2026-06-08

## Use Now

| Item | Role | Why |
| --- | --- | --- |
| GTSinger | Primary dataset | Paired speech/singing, alignments, technique labels, and existing local manifests. |
| WavLM Base+ | Primary SSL encoder | Local protocol already targets layers 3, 6, 9, 12; practical frozen-feature audit. |
| ECAPA-TDNN | Speaker baseline/evaluator | Existing repository evaluation already shows a speech/singing identity gap. |
| FACodec | Factorized-codec baseline | Public implementation and pretrained weights; directly probes content/prosody/timbre/detail streams. |

## Conditional

| Item | Role | Gate |
| --- | --- | --- |
| MSR-Codec | Multi-stream residual codec baseline | Clone/install/checkpoint smoke test must succeed before treating it as runnable. |
| ContentVec | Additional SSL/content baseline | Add only after WavLM+FACodec leakage cube works. |
| WavLM Large | Higher-capacity SSL baseline | Add only if GPU/time budget supports cached feature extraction. |

## Reference Only

| Item | Reason |
| --- | --- |
| AdaIN-VC | Important normalization prior art; no maintained official benchmark selected. |
| LoIN | Important local-statistics prior art; no maintained official implementation identified. |
| FreeCodec | Strong overlap, but visible repository has no usable code/checkpoints. |
| Privacy-preserving prosody representation learning | Current leakage/prosody precedent; no public code found. |
| Causal speaker leakage paper | Methodology precedent for linear/MLP probes and EER tradeoffs; no public code found. |
| SVCC 2025 systems and S2Voice | Evaluation references; not drop-in baselines for this task. |

