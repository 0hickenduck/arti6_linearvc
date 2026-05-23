# Gemini CLI VTuber Audio Extraction: Task Breakdown

## Context & Rules for Gemini (The Worker Bee)

This is a step-by-step implementation plan for building the VTuber audio extraction pipeline. You are acting as the executor.

**Critical Boundaries:**
1. **Do not delete raw data** or existing user work.
2. **Do not silently merge unverified data** into the final output. Always create a CSV/JSONL manifest first.
3. Always implement chunk-level processing, not just file-level processing.
4. **Validation First**: Produce intermediate CSV/JSONL files or small debug logs that can be inspected before running large batches.

**Target Grid per Speaker:**
* `en_speech` (10 chunks for PoC)
* `ja_speech` (10 chunks for PoC)
* `en_singing` (10 chunks for PoC)
* `ja_singing` (10 chunks for PoC)

Total PoC Target: 40 chunks for a single speaker.

---

## Step 1: Metadata Candidate Selection & Profiling

**Goal:** Classify existing videos and new candidate URLs into processing profiles based on metadata/titles.

**Implementation Details:**
1. Create a script (e.g., `scripts/data_collection/profile_videos.py`) that takes a list of URLs or local video metadata files.
2. The script must classify each video into one of the following `source_type`s:
   * `official_mv`: Mark `studio_like=true`. High audio quality, but post-produced.
   * `live_karaoke`: Best singing source.
   * `zatsudan`: Best speech source.
   * `game_stream`: Lower priority. Use if clean speech is scarce.
   * `collab`: Default exclude unless target speaker cluster confirmed.
   * `short_clip`: Exclude from primary data (mark as requires manual approval).
3. The script should also predict a coarse `language_candidate` (e.g., from title language or transcript).
4. **Output:** Generate a `video_manifest.csv` containing video ID, URL, `source_type`, and `language_candidate`.

**Validation Command:**
```bash
python3 scripts/data_collection/profile_videos.py --input candidate_urls.txt --output video_manifest.csv
head -n 20 video_manifest.csv
```

## Step 2: Audio Cleaning & Source-Type Routing

**Goal:** Route audio through different separation and cleaning paths based on `source_type`.

**Implementation Details:**
1. Update or create `scripts/data_collection/clean_audio.py`.
2. Implement conditional logic based on `source_type`:
   * `official_mv` & `live_karaoke`: Run Demucs/MDX to isolate vocals.
   * `zatsudan` & `game_stream`: Do not run Demucs by default (unless BGM is strong). Run Voice Activity Detection (VAD) first.
   * Special case: If `song_type=anthem` or `song_type=special`, tag clearly and do not mix with ordinary karaoke. Reject choir/group overlap.
3. **Output:** Cleaned audio files, mapped in an updated manifest `cleaned_manifest.csv`.

**Validation Command:**
```bash
python3 scripts/data_collection/clean_audio.py --manifest video_manifest.csv --output_dir data/cleaned/
ls data/cleaned/
```

## Step 3: Chunking & Quality Filtering

**Goal:** Break continuous audio into 3-12 second chunks and filter out low-quality segments.

**Implementation Details:**
1. Create `scripts/data_collection/chunk_audio.py`.
2. Use VAD and silence detection to split audio into chunks.
3. Apply Quality Filtering:
   * Reject chunks < 3 seconds or > 12 seconds.
   * Reject chunks with clipping, severe reverb, or obvious compression artifacts.
   * (Placeholder for future) Reject likely guest/second speaker and strong BGM leakage.
4. **Output:** A directory of `.wav` chunks and a `chunk_manifest.csv` with columns: `video_id`, `start_s`, `end_s`, `duration_s`, `chunk_path`, `source_type`.

**Validation Command:**
```bash
python3 scripts/data_collection/chunk_audio.py --manifest cleaned_manifest.csv --output_dir data/chunks/
wc -l chunk_manifest.csv
```

## Step 4: Language & Domain (Speech vs. Singing) Classification

**Goal:** Accurately label each chunk as English/Japanese and Speech/Singing.

**Implementation Details:**
1. Update `scripts/data_collection/classify_audio.py`.
2. Fix the bug where `is_singing` always returns `True`. Use a robust heuristic or a lightweight model to distinguish speech from singing.
3. Run language ID (e.g., Whisper langid or similar) on the chunk to determine `language_final` (`en`, `ja`, or `unknown`).
4. Update the manifest with: `domain_final` (speech/singing) and `language_final` (`en`/`ja`).
5. Filter out chunks with low language confidence or `unknown` language.

**Validation Command:**
```bash
python3 scripts/data_collection/classify_audio.py --manifest chunk_manifest.csv --output classified_chunk_manifest.csv
grep -E "en_speech|ja_speech|en_singing|ja_singing" classified_chunk_manifest.csv | head
```

## Step 5: Speaker Verification & Final Dataset Assembly

**Goal:** Ensure the target speaker is the dominant voice and assemble the 4-cell target grid.

**Implementation Details:**
1. Create `scripts/data_collection/assemble_dataset.py`.
2. Implement a placeholder or lightweight speaker verification step: assign a `speaker_score` to reject guest voices.
3. Filter the manifest to meet the requirements of the 4 cells (`en_speech`, `ja_speech`, `en_singing`, `ja_singing`).
4. **Proof of Concept Target:** Select exactly 10 high-quality chunks for each of the 4 cells for a single target speaker.
5. **Output:** `final_dataset_manifest.csv` adhering to the full PRD schema:
   * `speaker_id`, `video_id`, `url`, `source_type`, `domain_candidate`, `domain_final`, `language_candidate`, `language_final`, `song_type`, `start_s`, `end_s`, `duration_s`, `audio_path`, `speaker_score`, `language_confidence`, `singing_confidence`, `quality_score`, `rejection_reason`.

**Validation Command:**
```bash
python3 scripts/data_collection/assemble_dataset.py --manifest classified_chunk_manifest.csv --target_speaker <SPEAKER_ID> --output final_dataset_manifest.csv
awk -F, '{print $8, $6}' final_dataset_manifest.csv | sort | uniq -c
# Expected output should show ~10 for each of the 4 combinations
```
