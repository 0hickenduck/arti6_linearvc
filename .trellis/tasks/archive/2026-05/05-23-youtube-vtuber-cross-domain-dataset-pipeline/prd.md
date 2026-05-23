# PRD: YouTube VTuber Cross-Domain Dataset Pipeline (POC)

## Objective
Build an automated, rate-limit-safe pipeline to mine, download, and purify a highly-targeted Proof-of-Concept (POC) dataset of bilingual (EN/JP) VTubers. The dataset must capture the exact same speaker across two orthogonal axes: **Domain (Speech vs. Singing)** and potentially **Language (EN vs. JP)**.

This dataset will be used to demonstrate the vulnerability of current speaker-identity models under extreme domain shifts and to provide remedial training data for evaluating Voice Conversion models.

## Scope (Proof of Concept)
The initial pipeline will focus on a **micro-probe**:
*   **Target Size:** 2-3 specific VTuber channels (e.g., 1 EN bilingual, 1 JP bilingual).
*   **Data per Target:** 1 Chat/Zatsudan stream (Speech) and 1 Karaoke stream (Singing).
*   **Total Audio Size:** < 100MB per video (Opus/M4A audio only). Total expected footprint < 1GB.

## Components & Architecture

### 1. `scrape_vtuber_audio.py` (The Scraper)
*   **Tool:** Wrapper around `yt-dlp`.
*   **Input:** A list of Channel URLs or specific Video URLs, along with target tags (e.g., "Speech", "Singing", "EN", "JP").
*   **Behavior:**
    *   Downloads **audio-only** tracks (`bestaudio`).
    *   Saves associated metadata (Channel ID, Video ID, upload date) to a `.json` manifest.
*   **Safety/Anti-Ban Mechanisms:**
    *   Mandatory `--sleep-requests` (e.g., 15-30 seconds between calls).
    *   No parallel downloading.
    *   Ability to resume interrupted downloads.

### 2. `purify_audio.py` (The Purifier)
*   **Tool:** `HTDemucs` (or `UVR` CLI via python subprocess) and `Silero VAD`.
*   **Input:** The raw audio files and metadata manifest from Step 1.
*   **Behavior:**
    *   **Source Separation:** Passes the raw audio through Demucs to extract the `vocals` stem, discarding BGM and accompaniment.
    *   **Voice Activity Detection (VAD):** Processes the `vocals` stem with Silero VAD to slice the audio into clean, non-silent chunks (e.g., 3-15 seconds each).
    *   **Output:** A directory of clean `.wav` chunks organized by `ChannelID/Domain/VideoID_chunkXXX.wav`.

### 3. Intra-Channel Clustering (Deferred to Phase 2)
*   *Note: For the POC, if we manually select videos that are primarily solo streams, we can defer the automated "Guest Removal" clustering step until the pipeline is scaled.*

## Success Criteria for POC
1.  The scraper successfully downloads 4 targeted videos (audio only) without triggering YouTube rate limits.
2.  The purifier successfully outputs a directory of clean vocal `.wav` chunks.
3.  The output chunks correctly preserve the original domain (singing vs. speaking) and are audibly free of severe BGM interference.

## Next Steps
Once this PRD is approved, the developer (or subagent) will implement the `scrape_vtuber_audio.py` script as the first deliverable.