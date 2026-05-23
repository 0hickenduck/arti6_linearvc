# Gemini CLI VTuber Audio Extraction Workplan

## Goal

Create a Gemini CLI handoff plan for building a clean same-person
speech/singing and English/Japanese audio extraction pipeline from large VTuber
video collections. The pipeline should produce a small but reliable dataset for
identity-robustness and Seed-VC prompt experiments, not a generic video
downloader.

Target research grid per speaker:

```text
en_speech / ja_speech / en_singing / ja_singing
```

## What I Already Know

* Existing scripts live under `scripts/data_collection/`.
* Current scraper uses `yt-dlp` and cookies via `cookies_netscape.txt`.
* Current batch pipeline runs one broad path: download/copy -> Demucs vocal
  isolation -> Whisper language detection -> copy clean file.
* Current `classify_audio.py` always returns `is_singing: True`; this is a known
  blocker for speech/singing separation.
* Existing local data includes raw audio, cleaned audio, trimmed audio, and one
  Seed-VC VTuber demo output.
* The immediate research need is clean, chunk-level, same-person data across
  language and vocal mode.

## Requirements

### R1. Video-Type-Aware Extraction

The pipeline must classify each source video into one of these processing
profiles before audio cleaning:

| Source type | Examples | Main path | Notes |
| --- | --- | --- | --- |
| `official_mv` | official MV, polished cover | download audio -> Demucs/MDX vocal separation -> conservative chunking | High audio quality, but post-produced and often layered. Mark as `studio_like=true`. |
| `live_karaoke` | karaoke stream, singing stream | download audio -> Demucs/MDX vocal separation -> segment singing regions -> quality filter | Best singing source for this project. |
| `zatsudan` | chatting, free talk, reading | download audio -> VAD first -> optional denoise -> speaker filter | Best speech source. Do not run Demucs unless BGM is strong. |
| `game_stream` | gameplay with speech | VAD -> game-noise/music rejection -> speaker filter | Lower priority. Use only if clean speech is scarce. |
| `collab` | guest/collaboration/interview | diarization or speaker clustering required | Default exclude unless target speaker cluster is confirmed. |
| `short_clip` | Shorts, fan clips | metadata/candidate discovery only | Do not use as primary data unless manually approved. |

### R2. Multi-Language Handling

The pipeline must support English and Japanese chunks, including mixed-language
videos:

* Use metadata/title/transcript/Gemini CLI for coarse video-level language
  hints.
* Use ASR/language ID at chunk level for final labels.
* Permit mixed videos, but each final chunk must have one dominant language:
  `en`, `ja`, or `unknown`.
* Store both video-level candidate language and chunk-level detected language.

### R3. Anthem / Special Singing Handling

Anthem, national-song, ceremonial, and highly arranged singing should be
allowed but clearly tagged:

* `song_type=anthem` or `song_type=special`.
* Reject choir/group singing unless target voice is isolated and dominant.
* Keep these chunks for analysis/demo, but do not mix them with ordinary
  karaoke when training or computing primary statistics.

### R4. Chunk-Level Manifest

All final audio chunks must be represented in a JSONL or CSV manifest with at
least:

```text
speaker_id
video_id
url
source_type
domain_candidate
domain_final
language_candidate
language_final
song_type
start_s
end_s
duration_s
audio_path
speaker_score
language_confidence
singing_confidence
quality_score
rejection_reason
```

### R5. Quality Filtering

The pipeline should reject or downgrade chunks with:

* duration shorter than 3 seconds or longer than 12 seconds;
* likely guest/second speaker;
* strong BGM leakage for speech chunks;
* choir or multi-voice overlap for singing chunks;
* clipping, severe reverb, or obvious compression artifacts;
* language uncertainty when the target cell requires English or Japanese.

### R6. Gemini CLI Usage

Gemini CLI should be used as an agent for high-volume, lower-risk tasks:

* inventory existing scripts and outputs;
* inspect video metadata/title/transcript and propose source-type labels;
* generate candidate manifests from existing large video lists;
* implement isolated scripts according to this PRD;
* summarize batch results and flag suspicious chunks.

Gemini should not make irreversible changes, delete raw data, or silently mix
unverified chunks into the final dataset.

## Acceptance Criteria

* [ ] A Gemini-readable handoff file exists with ordered subtasks and exact
  prompts.
* [ ] The task plan separates metadata candidate selection, audio cleaning,
  chunking, language/domain classification, speaker verification, and final
  dataset assembly.
* [ ] The plan explicitly handles `official_mv`, `live_karaoke`, `zatsudan`,
  `game_stream`, `collab`, and `short_clip`.
* [ ] The plan defines the four-cell output grid:
  `en_speech`, `ja_speech`, `en_singing`, `ja_singing`.
* [ ] The plan gives Gemini clear implementation boundaries and validation
  commands.
* [ ] The plan includes a minimal 40-chunk proof-of-concept target: one speaker,
  10 clean chunks per cell.

## Definition of Done

* PRD and Gemini task breakdown are written under this task directory.
* Implementation/check context points to the relevant specs and plan files.
* No raw data or existing user work is deleted.
* The next agent can start from the task breakdown without re-reading the full
  conversation.

## Out of Scope

* Training a large model from scratch.
* Fully automated legal/copyright resolution.
* Claiming a publishable dataset before manual identity/quality checks.
* Using collab/game streams as primary data before diarization or clustering is
  reliable.

## Technical Notes

Relevant existing files:

* `scripts/data_collection/scrape_youtube.py`
* `scripts/data_collection/batch_process.py`
* `scripts/data_collection/pipeline.py`
* `scripts/data_collection/classify_audio.py`
* `scripts/run_vtuber_demo.py`

Known implementation gaps:

* Current classification does not detect speech vs singing.
* Current batch output is file-level, not chunk-level.
* Current data cleaning does not choose different processing paths per video
  type.
* Speaker verification and guest filtering are not yet part of the pipeline.

