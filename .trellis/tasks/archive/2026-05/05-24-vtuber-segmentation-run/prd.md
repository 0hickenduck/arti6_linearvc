# VTuber Segmentation Run

## Goal

Run the current conservative segmentation strategy on existing local VTuber WAVs
and existing Demucs vocal stems, without moving project directories and without
downloading new YouTube audio.

## What I Already Know

* The repo has already been soft-split into Trellis packages, but script paths
  still intentionally point at `vtuber_pipeline/` and `data/`.
* There are 51 raw WAVs under `data/raw_audio`.
* Every raw WAV has a matching `_vocals.wav` stem in the known Demucs stem
  directories.
* 20 raw WAVs are longer than 1200 seconds, mostly long talking streams.
* The previous conservative run exists at `data/vtuber_curated_conservative/`.
* The user wants to start segmentation now and defer physical project-path
  refactoring until after current data-flow scripts are finished.

## Assumptions

* Use the current conservative acoustic-vocal-activity strategy.
* Do not overwrite the previous auditioned output directory.
* Keep `--max-source-sec 1200` for this run so long zatsudan/talking streams
  stay out until diarization or target-speaker verification is added.
* Use existing Demucs stems from `data/temp_demucs` and `data/demucs_tmp`.

## Requirements

* Run segmentation from existing WAVs only.
* Produce a new output snapshot under `data/`.
* Preserve manifest traceability for source path, processing stem, status,
  timestamps, and segmentation strategy.
* Keep singing segmentation independent of ASR transcript content.
* Keep ambiguous/multi-speaker material in review or quarantine.

## Acceptance Criteria

* [ ] Segmentation command completes successfully.
* [ ] `summary.json`, `sources.json`, `skipped_sources.json`, and
  `manifest.jsonl` are generated.
* [ ] Manifest row count matches generated WAV count.
* [ ] No generated WAV is zero bytes.
* [ ] Long sources skipped by `--max-source-sec 1200` are recorded.

## Out Of Scope

* Physical project directory migration.
* New YouTube downloads.
* Diarization or target-speaker verification for long talking streams.
* Manual relabeling of Kiara language/domain errors.
* Training a model.
