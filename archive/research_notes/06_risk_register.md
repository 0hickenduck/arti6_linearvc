# Risk Register

Status: PARTIAL GO

| Risk | Likely impact | Early detection | Mitigation | Status |
|---|---|---|---|---|
| ARTI-6 checkpoint unavailable | Cannot run inversion or synthesis. | Repository README/source references unavailable checkpoint path or gated asset. | Ask for checkpoint source; do not download without approval. | OPEN |
| ARTI-6 API different from assumptions | Planned scripts and artifact names may be wrong. | Gate 1 repo audit fails to find expected inversion/synthesis entrypoints. | Read source and adapt commands to verified API only. | OPEN |
| Hugging Face login required | Checkpoint or model dependency may be inaccessible. | Download or model load errors mention auth/token/gated repo. | Ask user for approved access path or alternative checkpoint. | OPEN |
| WavLM-large download failure | Speaker embedding dependency may fail or be too large. | Import/model load attempts request large remote asset. | Ask before download; prefer cached path or defer WavLM-dependent steps. | OPEN |
| CUDA/PyTorch mismatch | Runtime may fail at import or inference. | Errors mention CUDA version, torch binary, missing GPU, or driver. | Use CPU if supported; otherwise move to lab server after environment audit. | OPEN |
| CMU ARCTIC path mismatch | Manifest creation fails. | `find` cannot locate bdl/slt wavs or prompt IDs. | Inspect actual dataset layout and update manifest logic. | OPEN |
| Input wav sample rate mismatch | ARTI-6 preprocessing or synthesis may fail or degrade output. | Audio loader reports unexpected sample rate or model rejects input. | Resample according to verified ARTI-6 preprocessing requirements. | OPEN |
| Target speaker embedding dominates VC | Articulatory transform may not add audible effect. | Embedding-only and transform-plus-target-speaker sound nearly identical. | Make this the main ablation; inspect diagnostics before claiming contribution. | OPEN |
| 6D articulatory transform has weak audible effect | Research claim may be weak or limited to diagnostics. | Transformed trajectories differ but audio barely changes. | Report as feasibility finding; consider richer transforms later. | OPEN |
| Paired utterance alignment insufficient | Diagonal/full affine fitting may learn artifacts. | Source/target frame counts differ or normalized trajectories look distorted. | Start with mean/std transform; treat alignment-based methods as secondary. | OPEN |
| Length normalization creates artifacts | Converted audio may sound unstable. | Diagnostics show unnatural trajectory jumps or compressed dynamics. | Compare against mean/std no-alignment baseline; use smoother interpolation if needed. | OPEN |
| Synthesis API may require normalized feature ranges | Direct transformed features may be out of distribution. | Synthesis fails or audio clips/noises; tensor range differs from training range. | Inspect ARTI-6 normalization code and clamp/normalize only if verified. | OPEN |

## Reporting Rule

Every failure must include:

- exact error
- likely cause
- next diagnostic command
- minimal fix
- GO / PARTIAL GO / BLOCKED status
