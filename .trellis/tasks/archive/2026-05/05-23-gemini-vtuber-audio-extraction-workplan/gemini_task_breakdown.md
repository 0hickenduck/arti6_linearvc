# Gemini CLI Task Breakdown

This file is the direct handoff for Gemini CLI. The parent goal is to build a
clean same-person EN/JP speech/singing extraction pipeline from VTuber videos.

Use the local Gemini delegation command from `AGENTS.md`:

```bash
~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh \
  --model flash \
  --prompt "<instructions>"
```

Use `--model flash` for reading, inventory, metadata screening, and summaries.
Use `--model pro` only for larger code edits.

Important constraints for Gemini:

* You are not alone in the repo. Do not revert edits made by others.
* Do not delete raw data or existing outputs.
* Prefer adding new scripts or narrowly modifying existing data-collection
  scripts.
* Preserve provenance: every output chunk must trace back to source video,
  start/end time, and classification scores.
* Commit only if the parent explicitly asks; otherwise report changed files and
  validation commands.

## Target Output

For each accepted speaker, build this dataset grid:

```text
data/vtuber_grid/<speaker_id>/
  en_speech/
  ja_speech/
  en_singing/
  ja_singing/
  manifest.jsonl
  summary.json
```

Minimal proof-of-concept target:

* one speaker;
* 10 clean chunks per cell;
* chunk duration 3-12 seconds;
* all chunks manually spot-checkable through manifest paths.

## Video-Type Policy

Gemini must classify candidate videos before audio extraction:

| source_type | Use | Processing policy |
| --- | --- | --- |
| `official_mv` | Useful singing, but post-produced | Download audio, separate vocals, conservative quality filter, tag `studio_like=true`. |
| `live_karaoke` | Primary singing source | Download audio, separate vocals, segment singing, reject talking/noise/choir. |
| `zatsudan` | Primary speech source | VAD first, optional denoise, no Demucs unless BGM is strong. |
| `game_stream` | Backup speech source | VAD + noise rejection; use only if zatsudan is insufficient. |
| `collab` | Normally excluded | Requires diarization or speaker-cluster filtering. |
| `short_clip` | Candidate discovery only | Do not use as primary training/eval data unless manually approved. |

## Task 0: Inventory Existing State

Purpose: avoid duplicating work and identify current broken assumptions.

Suggested Gemini CLI command:

```bash
~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model flash --prompt "
In /home/bowen/bowen_lab/projects/arti6_linearvc, inspect the existing VTuber data-collection code and outputs. Do not edit files.

Read:
- scripts/data_collection/*.py
- scripts/run_vtuber_demo.py
- data/raw_audio/download_stats.json
- data/vtuber_clean/batch_summary.json if present
- data/vtuber_trimmed/batch_summary.json if present

Return:
1. What scripts exist and what each currently does.
2. Current output directories and what they contain.
3. Known blockers for producing en_speech / ja_speech / en_singing / ja_singing.
4. Which files should be modified or added next.
"
```

Expected finding: `classify_audio.py` currently marks everything as
`is_singing=True`, so it cannot be trusted for domain labels.

## Task 1: Build Candidate Manifest From Existing Video Resources

Purpose: create a structured candidate list before downloading or cleaning more
audio.

Deliverable:

```text
data/manifests/vtuber_video_candidates.jsonl
```

Each row:

```json
{
  "speaker_id": "Mori",
  "video_id": "...",
  "url": "https://www.youtube.com/watch?v=...",
  "title": "...",
  "duration_s": 1234,
  "source_type_candidate": "zatsudan",
  "language_candidate": "en",
  "domain_candidate": "speech",
  "risk_flags": ["solo_likely"],
  "priority": 4,
  "notes": "why this was selected"
}
```

Gemini work:

* Use existing directory names under `data/raw_audio/<speaker>/<category>/`.
* Use any existing metadata if available; otherwise infer only from path, video
  ID, and category folder.
* If title metadata is missing, create a placeholder and mark
  `metadata_missing=true`.
* Do not download new audio in this task.

Validation:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('data/manifests/vtuber_video_candidates.jsonl')
rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
assert rows
required = {'speaker_id','video_id','source_type_candidate','language_candidate','domain_candidate','priority'}
for row in rows:
    assert required <= row.keys(), row
print('candidate rows', len(rows))
PY
```

## Task 2: Implement Source-Type Routing

Purpose: stop treating every video the same.

Suggested new script:

```text
scripts/data_collection/route_audio_extraction.py
```

CLI shape:

```bash
.venv/bin/python scripts/data_collection/route_audio_extraction.py \
  --manifest data/manifests/vtuber_video_candidates.jsonl \
  --raw-root data/raw_audio \
  --output-root data/vtuber_routed \
  --limit 8
```

Behavior:

* `official_mv` and `live_karaoke`: run vocal separation first, then segment.
* `zatsudan`: run VAD first; skip Demucs unless `music_heavy=true`.
* `game_stream`: run VAD first, then stricter noise filtering.
* `collab`: skip by default with `rejection_reason=needs_diarization`.
* `short_clip`: skip by default with `rejection_reason=candidate_only`.

Output:

```text
data/vtuber_routed/
  chunks/
  routed_manifest.jsonl
  summary.json
```

Each output row should preserve the candidate row fields and add:

```text
audio_path
start_s
end_s
duration_s
processing_profile
rejection_reason
```

Implementation note:

* Reuse existing `isolate_vocals.py`, `remove_silence.py`, or
  `segment_audio.py` when practical.
* If VAD utilities are incomplete, implement a small conservative
  energy/VAD-based segmenter first; do not block on perfect diarization.

## Task 3: Replace Naive Domain and Language Classification

Purpose: produce credible `speech` vs `singing` and `en` vs `ja` labels.

Modify or replace:

```text
scripts/data_collection/classify_audio.py
```

Required output per chunk:

```json
{
  "language_final": "en",
  "language_confidence": 0.91,
  "domain_final": "speech",
  "singing_confidence": 0.12,
  "classification_notes": "ASR language en; low sustained-pitch proxy"
}
```

Minimum acceptable heuristic for POC:

* Language: Whisper/faster-whisper language detection on each chunk.
* Speech/singing:
  * use source-type prior (`zatsudan` strongly speech, `live_karaoke` strongly
    singing);
  * combine with audio features: voiced duration, pitch stability, sustained
    voiced frames, and ASR density;
  * expose confidence rather than hard pretending.

Important:

* Never return `is_singing=True` for every file.
* If uncertain, set `domain_final=unknown` and keep the chunk out of the final
  four-cell dataset.

Validation:

```bash
.venv/bin/python scripts/data_collection/classify_audio.py --help
python3 -m compileall -q scripts/data_collection
```

## Task 4: Add Speaker Verification / Guest Filtering

Purpose: verify that chunks are the target person.

Suggested script:

```text
scripts/data_collection/filter_target_speaker.py
```

CLI shape:

```bash
.venv/bin/python scripts/data_collection/filter_target_speaker.py \
  --manifest data/vtuber_routed/routed_manifest.jsonl \
  --reference-manifest data/manifests/vtuber_reference_chunks.jsonl \
  --output data/vtuber_routed/speaker_filtered_manifest.jsonl
```

Behavior:

* Build one speaker centroid per `speaker_id` from manually trusted reference
  chunks.
* Score every candidate chunk against that centroid using ECAPA or WavLM speaker
  embeddings.
* Mark likely guest/mismatch chunks with `rejection_reason=speaker_mismatch`.
* Keep scores in the manifest; do not delete chunk files.

Acceptance:

* Works on a small manifest.
* Does not require all speakers to have references; missing references should
  produce clear skipped rows.

## Task 5: Assemble the Four-Cell Dataset

Purpose: create the actual research artifact.

Suggested script:

```text
scripts/data_collection/build_vtuber_grid_dataset.py
```

CLI shape:

```bash
.venv/bin/python scripts/data_collection/build_vtuber_grid_dataset.py \
  --manifest data/vtuber_routed/speaker_filtered_manifest.jsonl \
  --output-root data/vtuber_grid \
  --speaker-id Mori \
  --chunks-per-cell 10
```

Selection rules:

* Required cells:
  * `en_speech`
  * `ja_speech`
  * `en_singing`
  * `ja_singing`
* Choose highest `quality_score` chunks.
* Reject `unknown` language/domain.
* Reject `collab`, `short_clip`, and uncertain speaker rows by default.
* Preserve source provenance in `manifest.jsonl`.

Output summary should report:

```text
speaker_id
num_en_speech
num_ja_speech
num_en_singing
num_ja_singing
missing_cells
mean_quality_score_by_cell
mean_speaker_score_by_cell
```

## Task 6: Build Evaluation Entry Points

Purpose: immediately answer whether the data is useful.

Deliverables:

1. Speaker embedding grid report:

```text
outputs/vtuber_grid_eval/<speaker_id>/summary.json
outputs/vtuber_grid_eval/<speaker_id>/index.html
```

Report pairwise similarity across:

```text
en_speech -> en_speech
en_speech -> ja_speech
en_speech -> en_singing
en_speech -> ja_singing
en_singing -> ja_singing
ja_speech -> ja_singing
```

2. Seed-VC prompt demo setup:

Create a manifest for running:

* source singing -> target EN speech prompt;
* source singing -> target JP speech prompt;
* source singing -> target EN singing prompt;
* source singing -> target JP singing prompt.

The goal is not perfect synthesis. The goal is to measure whether same-person
speech prompts are weaker than same-person singing prompts, and whether language
changes make that gap larger.

## Task 7: Human Spot-Check Pack

Purpose: make manual listening efficient.

Generate:

```text
outputs/vtuber_grid_review/<speaker_id>/review.html
outputs/vtuber_grid_review/<speaker_id>/review_manifest.jsonl
```

The page should show grouped audio players by cell with:

* source video id;
* start/end time;
* language/domain labels;
* speaker score;
* quality score;
* quick reject reason field in JSON manifest format.

This is essential because the final dataset must not rely only on automatic
labels.

## Recommended Execution Order

1. Task 0: inventory.
2. Task 1: candidate manifest.
3. Task 3: fix classification API first, because current labels are wrong.
4. Task 2: routing + chunking.
5. Task 4: speaker filtering.
6. Task 5: four-cell dataset.
7. Task 6: objective eval + Seed-VC prompt manifest.
8. Task 7: review HTML.

## Gemini Prompt For First Implementation Pass

Use this after Task 0:

```bash
~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model pro --prompt "
You are working in /home/bowen/bowen_lab/projects/arti6_linearvc.

Read:
- .trellis/tasks/05-23-gemini-vtuber-audio-extraction-workplan/prd.md
- .trellis/tasks/05-23-gemini-vtuber-audio-extraction-workplan/gemini_task_breakdown.md
- scripts/data_collection/*.py

Implement Task 1 and Task 3 only:
1. Create data/manifests/vtuber_video_candidates.jsonl from existing data/raw_audio layout and any available metadata. Do not download new audio.
2. Replace the naive classification behavior so classify_audio.py no longer labels every file as singing. Provide a CLI that can classify one file and return JSON.

Constraints:
- Do not delete existing data or outputs.
- Preserve existing imports where possible, but add clear argparse CLIs.
- Keep changes narrow.
- Run python3 -m compileall -q scripts/data_collection.

Return changed files, commands run, and any blockers.
"
```

