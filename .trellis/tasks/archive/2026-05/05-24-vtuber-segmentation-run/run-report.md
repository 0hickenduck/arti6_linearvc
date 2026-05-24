# VTuber Segmentation Run Report - 2026-05-24

## Command

```bash
.venv/bin/python vtuber_pipeline/src/curate_existing_audio.py \
  --input-dir data/raw_audio \
  --vocal-dir data/temp_demucs \
  --vocal-dir data/demucs_tmp \
  --output-dir data/vtuber_curated_conservative_20260524_run2 \
  --max-source-sec 1200
```

## Input Scan

* Raw WAVs: 51
* Raw WAVs with matched vocal stems: 51
* Long sources skipped by `--max-source-sec 1200`: 20
* Existing previous output preserved: `data/vtuber_curated_conservative/`

## Output

* Output directory: `data/vtuber_curated_conservative_20260524_run2/`
* Size: 379M
* Manifest: `data/vtuber_curated_conservative_20260524_run2/manifest.jsonl`
* Summary: `data/vtuber_curated_conservative_20260524_run2/summary.json`
* Sources: `data/vtuber_curated_conservative_20260524_run2/sources.json`
* Skipped sources: `data/vtuber_curated_conservative_20260524_run2/skipped_sources.json`

## Validation

* Manifest rows: 241
* Generated WAV files: 241
* Summary segment count: 241
* Zero-byte WAVs: 0
* Duration range: 3.100-15.000 seconds
* Mean duration: 9.310 seconds

Status counts:

* `clean_candidate`: 92
* `review`: 101
* `quarantine`: 48

Breakdown:

* `clean_candidate/Enna/EN_Singing`: 43
* `clean_candidate/Kiara/EN_JP_DE_Talking`: 6
* `clean_candidate/Kiara/EN_Singing`: 28
* `clean_candidate/Mori/EN_JP_Singing`: 15
* `quarantine/FuwaMoco/EN_JP_Singing`: 48
* `review/Enna/EN_Talking`: 10
* `review/Mori/EN_JP_Talking`: 91

## Decision

This run intentionally keeps the current path layout and does not move scripts
under `projects/`. Physical project refactoring should wait until this
segmentation/data-flow phase is stable, because the active scripts and manifests
still rely on `vtuber_pipeline/` and `data/` paths.
