# VTuber Voice Lane

Canonical code path: `vtuber_pipeline/`

Local-only generated outputs:

- `data/raw_audio/`
- `data/temp_demucs/`
- `data/demucs_tmp/`
- `data/vtuber_curated_conservative/`
- `data/vtuber_curated_conservative_20260524_run2/`

Current status:

- [progress.md](progress.md)

Research focus:

- multilingual speaking voice from messy YouTube sources
- multilingual singing voice from karaoke/MV/shorts sources
- conservative segmentation with review/quarantine buckets
- manifests that preserve source identity, timing, processing stage, and quality
  status

Generated audio directories should stay expanded by default so they can be
previewed on the server. Use archives only as temporary transfer packages or for
portable HTML demo bundles.
