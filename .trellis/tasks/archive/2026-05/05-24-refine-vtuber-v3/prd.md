# brainstorm: refine vtuber dataset curation and pipeline for version 3

## Goal

Based on the feedback from version 2 of the VTuber dataset, we want to refine both the data discovery pipeline and the curation logic to generate a high-quality **version 3** dataset. Specifically, we need to address short clips/mouth sounds for Kiara, missing speech for Enna & Mori, misclassified songs (like the Ethyria soundtrack), and twin identity separation for FuwaMoco.

## What I already know

Through research and analysis of the `run2` output, we discovered the following root causes:
1. **Kiara's Speech in `clean_candidate`**: These clips originated from YouTube Shorts (durations < 25 seconds). Shorts are highly edited and expressive (screams, mouth sounds, laughter) and do not represent stable talking voices for voice conversion.
2. **Missing Speech for Enna**: Enna's only downloaded speech file in `run2` was `2SZbnGJAymg` (187.4s), which is actually titled **"ETHYRIA (original soundtrack) Enna Alouette × keiki"** (a song!). It was misclassified as `EN_Talking` by the LLM in Step 1 (Discovery), and because its duration was > 180s (default `clean_speech_max_source_sec`), it was sent to the `review` folder with the reason `long_speech_needs_diarization`. Enna's actual 5-hour chatting stream (`7HOkTSZ3rCs`) was skipped entirely because it exceeded the source duration limit.
3. **Missing Speech for Mori**: All of Mori Calliope's speech segments were automatically sent to the `review` folder because of a hardcoded rule in `curate_existing_audio.py` that flags all Mori speech as `mori_talking_may_include_multiple_speakers`.
4. **FuwaMoco Quarantine**: FuwaMoco streams are twin streams with constant overlap, which are successfully quarantined as expected for now.

## Evolving Requirements

1. **Shorts / Clip Filtering**:
   - Filter out videos under 300 seconds (5 minutes) for the `Speech`/`Talking` domain during Discovery (`discover_videos.py`) and Curation (`curate_existing_audio.py`).
2. **Robust Classification**:
   - Instruct the Gemini classification model in `discover_videos.py` to be more conservative about songs, soundtracks, original soundtracks (OST), and MVs to prevent them from entering the `Speech` domain.
   - Extract video durations during `discover_videos.py` using `yt-dlp` flat playlist extraction to perform initial duration filtering before LLM classification.
3. **Speech Curation Enhancements**:
   - Add a `clean_speech_min_source_sec` filter (default 300s) to prevent short clips from ever becoming `clean_candidate` speech.
   - Adjust `clean_speech_max_source_sec` or diarization thresholds to allow moderate-length chatting videos (e.g. 5–15 minutes) to go straight to `clean_candidate`.
   - Provide override options or list verified solo chatting streams for Mori/Enna to bypass the hardcoded multi-speaker flags.
4. **Long Stream Handling**:
   - For long Zatsudan streams (e.g. Enna's 5-hour stream), design a strategy to selectively download or chunk/diarize them rather than skipping them entirely.

## Open Questions

1. **Speech Minimum Duration**: Is 5 minutes (300 seconds) an acceptable threshold for a solo chatting stream to ensure it is not a Short or highly edited clip?
2. **Override/Allow-list**: Would you prefer we maintain an explicit allow-list of verified solo chatting video IDs, or should we refine the heuristics to allow specific channels after manual check?
3. **Long Stream Strategy**: For very long streams (e.g., 2–5 hours), should we process a prefix (e.g. first 30 minutes) or download/segment them entirely (accepting higher compute/disk usage)?

## Acceptance Criteria

- [ ] `discover_videos.py` extracts video durations and filters out videos under 300s for the `Speech` domain.
- [ ] Gemini classification prompt refined to strongly reject music, covers, MV, and OST from the `Speech` category.
- [ ] `curate_existing_audio.py` filters speech inputs with a minimum duration constraint.
- [ ] Mori/Enna verified speech segments can bypass multi-speaker flags and be placed in `clean_candidate`.
- [ ] Complete pipeline rerun to generate VTuber dataset v3 with high-quality Speech & Singing domains.

## Out of Scope

- Full-scale diarization pipeline integration for multi-hour streams (this will be handled in a separate lane).
- Chorus separation/source separation for twin streams (FuwaMoco stays quarantined).

## Technical Notes

* Discovery script: [discover_videos.py](file:///home/bowen/bowen_lab/projects/arti6_linearvc/vtuber_pipeline/src/discover_videos.py)
* Scraper script: [scrape_vtuber_audio.py](file:///home/bowen/bowen_lab/projects/arti6_linearvc/vtuber_pipeline/src/scrape_vtuber_audio.py)
* Curation script: [curate_existing_audio.py](file:///home/bowen/bowen_lab/projects/arti6_linearvc/vtuber_pipeline/src/curate_existing_audio.py)
* Run2 Outputs: [summary.json](file:///home/bowen/bowen_lab/projects/arti6_linearvc/data/vtuber_curated_conservative_20260524_run2/summary.json)
