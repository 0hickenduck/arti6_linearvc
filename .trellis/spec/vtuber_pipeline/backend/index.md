# VTuber Pipeline Backend Guidelines

## Scope

Applies to code and documentation under `vtuber_pipeline/`, including YouTube
audio discovery, vocal isolation, segmentation, manifests, and local data
curation utilities.

## Pre-Development Checklist

Read these before editing the VTuber pipeline:

- `.trellis/spec/repo-structure.md`
- `.trellis/spec/research-safety.md`
- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/backend/logging-guidelines.md`

## Local Rules

- Keep raw audio, separated stems, generated datasets, and checkpoints out of
  git.
- Keep generated VTuber audio datasets as expanded directories by default so
  server-side audio preview works. Do not create persistent archives unless the
  user explicitly asks for transfer packaging or a portable demo/report bundle.
- Preserve source traceability through manifests whenever audio is copied,
  segmented, or filtered.
- For singing data, do not use ASR text as the main acceptance gate; keep
  singer-produced non-linguistic material when identity and quality are
  plausible.
- Put uncertain speaker identity, overlap, heavy chorus, and contaminated clips
  into review or quarantine rather than train-clean output.
