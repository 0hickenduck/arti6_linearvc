# Track 2: Technique Probing & Reconstruction

**Goal:** Find linear directions for singing techniques (vibrato, falsetto, breathy, etc.) in frozen SSL representations, then steer downstream synthesis.

## Status
🟡 Ready to implement (activate if Track 1 go/no-go fails)

## Entry Point
See [`../design/CODEX_INSTRUCTIONS.md`](../design/CODEX_INSTRUCTIONS.md) Section 4 for full step-by-step.

## Outputs (will be created here)
- `manifests/phoneme_pairs.parquet` — same-phoneme, different-technique pairs from GTSinger
- `features/` — cached frozen SSL frame-level features
- `results/` — direction stability figures, steering audio samples
