# Track 1: Timbre Mode Residual

**Goal:** Map the vocal identity shift when a person moves from speech to singing ($\Delta = T_{\text{singing}} - T_{\text{speech}}$), then use it to improve zero-shot SVC when only target speech is available.

## Status
🟡 Ready to implement

## Entry Point
See [`../design/CODEX_INSTRUCTIONS.md`](../design/CODEX_INSTRUCTIONS.md) Section 3 for full step-by-step.

## Outputs (will be created here)
- `manifests/utterances.parquet` — the dataset manifest
- `features/` — cached frozen SSL embeddings
- `results/` — probe figures, audio pairs, decision memo
