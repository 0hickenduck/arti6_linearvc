# Conservative Segmentation Run - 2026-05-24

## Command

```bash
.venv/bin/python vtuber_pipeline/src/curate_existing_audio.py \
  --input-dir data/raw_audio \
  --vocal-dir data/temp_demucs \
  --vocal-dir data/demucs_tmp \
  --output-dir data/vtuber_curated_conservative \
  --max-source-sec 1200 \
  --skip-existing
```

## Output

* Output directory: `data/vtuber_curated_conservative/`
* Manifest: `data/vtuber_curated_conservative/manifest.jsonl`
* Summary: `data/vtuber_curated_conservative/summary.json`
* Source detail: `data/vtuber_curated_conservative/sources.json`
* Skipped long-source list: `data/vtuber_curated_conservative/skipped_sources.json`

## Counts

* Source WAVs processed: 31
* Source WAVs skipped by `--max-source-sec 1200`: 20
* Total segments: 241
* Segment duration range: 3.100-15.000 seconds
* Mean segment duration: 9.310 seconds

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

## Interpretation

This run reused existing Demucs vocal stems whenever possible and did not run Whisper/ASR as a singing gate. Singing chunks were segmented by energy-based vocal activity with wider gap merging and padding than the earlier ASR/VAD pass.

Conservative identity policy:

* FuwaMoco singing is `quarantine` because the channel is intentionally multi-speaker/twin identity.
* Mori talking is `review` because the user observed multi-speaker contamination risk in those videos.
* Long talking streams were skipped for this pass because they need diarization or target-speaker verification before producing train-clean chunks.

No zero-byte WAV outputs were found in the generated segment set.

## User Listening Feedback - 2026-05-24

The user listened to representative outputs from this conservative pass.

Observations to keep:

* Singing sounds better than the earlier aggressive linguistic-content cut.
* BGM-only regions are mostly removed while musical phrasing is more comfortable.
* Reverb and backing/harmony vocals remain; this is acceptable for now when the
  source/device/reverb condition is consistent and can be treated as part of the
  observed singing timbre.
* Kiara shorts still have unreliable language/domain labels. Some Japanese songs
  are labeled as English, and some clips are non-linguistic murmuring.

Decision:

* Do not rerun segmentation immediately.
* Keep the current output as a usable conservative candidate/review set.
* Address language labeling and Kiara shorts cleanup in a later pass, likely with
  metadata/manual correction rather than treating ASR language as authoritative
  for singing.
