# VTuber End-to-End Data Pipeline

This package contains the automated tools for discovering, scraping, purifying, and segmenting VTuber audio into clean datasets for voice conversion research.

## Quick Start (The "One-Click" Agent)

You can run the entire pipeline—from AI video discovery all the way to uploading the final clean dataset to your server—using the local orchestrator agent.

### Prerequisites

1. Install requirements on your local machine:
   ```bash
   pip install yt-dlp google-genai pydantic torch torchaudio
   ```
2. You need `ffmpeg` installed on your system.
3. (Optional but recommended) Put your YouTube cookies into `vtuber_pipeline/cookies_netscape.txt` to bypass age/member restrictions.

### Running the Agent

1. Set your Gemini API key (for the AI video discovery):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

2. (Optional) Set your upload credentials. If you set these, the agent will automatically `scp` the final `.tar.gz` dataset to your server. If you leave them empty, it will just leave the `.tar.gz` on your local machine.
   ```bash
   export UPLOAD_SERVER_IP="192.168.1.100"
   export UPLOAD_SERVER_USER="bowen"
   export UPLOAD_SERVER_PATH="/home/bowen/vtuber_datasets/"
   ```

3. Run the orchestrator with the target YouTube channel URL:
   ```bash
   python3 vtuber_pipeline/src/local_agent.py "https://www.youtube.com/@EnnaAlouette" --max-videos 20
   ```

### What it does automatically:
1. **Discovery:** Calls Gemini Flash to look at the channel's recent 20 videos, avoiding collabs and cleanly separating `Speech` (Zatsudan) from `Singing` (Karaoke).
2. **Download:** Uses `yt-dlp` to download the audio tracks.
3. **Purify:** Runs Demucs to strip background music, and Silero VAD to slice the audio into clean 3-15 second chunks.
4. **Archive:** Zips all the clean chunks into `data/dataset_EnnaAlouette_YYYYMMDD.tar.gz`.
5. **Upload:** Uses SCP to securely send the `.tar.gz` to your server.

## Conservative Segmentation From Existing WAVs

When raw WAVs and Demucs vocal stems already exist, run the conservative curation pass instead of downloading again:

```bash
.venv/bin/python vtuber_pipeline/src/curate_existing_audio.py \
  --input-dir data/raw_audio \
  --vocal-dir data/temp_demucs \
  --output-dir data/vtuber_curated_conservative \
  --max-source-sec 1200
```

This pass uses existing `<video_id>_vocals.wav` files when available. Singing is segmented by vocal activity and phrase continuity, not by ASR text, so non-lexical target vocal material such as sustained notes, humming, breaths, and ad libs is not discarded only because Whisper cannot transcribe it.

Outputs are split into `clean_candidate/`, `review/`, and `quarantine/`, with a JSONL manifest recording source video id, timestamps, processing source, and the reason for each status.
