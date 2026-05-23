# YouTube VTuber Cross-Domain Dataset Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a rate-limit-safe Python pipeline to download audio-only streams from specific YouTube URLs and separate them into clean vocal chunks using HTDemucs and VAD.

**Architecture:** A two-script pipeline. The first script uses `yt-dlp` to fetch audio tracks and metadata with enforced delays to prevent rate-limiting. The second script uses a subprocess call to `demucs` to isolate vocals and `silero-vad` (via `torchaudio`) to chunk the vocals into non-silent `.wav` segments.

**Tech Stack:** Python 3.10+, `yt-dlp`, `demucs`, `torchaudio` (for Silero VAD), `soundfile`.

---

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `arti6_linearvc_demo/pipeline_requirements.txt`
- Create: `arti6_linearvc_demo/dataset_manifest.json`

- [ ] **Step 1: Define dependencies**

Write the required pip packages to `arti6_linearvc_demo/pipeline_requirements.txt`:

```text
yt-dlp
demucs
torchaudio
soundfile
tqdm
```

- [ ] **Step 2: Create the initial manifest file**

Create the JSON file `arti6_linearvc_demo/dataset_manifest.json` with 2 dummy targets to test the scraper logic. We will use short CC-licensed or well-known short clips for testing.

```json
[
  {
    "channel_id": "TEST_CHANNEL_1",
    "video_id": "BaW_jenozKc",
    "url": "https://www.youtube.com/watch?v=BaW_jenozKc",
    "domain": "speech",
    "language": "en"
  },
  {
    "channel_id": "TEST_CHANNEL_1",
    "video_id": "dQw4w9WgXcQ",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "domain": "singing",
    "language": "en"
  }
]
```

- [ ] **Step 3: Commit**

```bash
git add arti6_linearvc_demo/pipeline_requirements.txt arti6_linearvc_demo/dataset_manifest.json
git commit -m "chore: setup dependencies and test manifest for dataset pipeline"
```

---

### Task 2: Implement the Scraper (`scrape_vtuber_audio.py`)

**Files:**
- Create: `arti6_linearvc_demo/scrape_vtuber_audio.py`

- [ ] **Step 1: Write the scraper script**

Create `arti6_linearvc_demo/scrape_vtuber_audio.py` that reads the manifest, initializes `yt_dlp.YoutubeDL` with strict rate-limit settings, and downloads the best audio as `opus`/`m4a` into a raw directory.

```python
import json
import os
import time
import random
import yt_dlp

def scrape_audio(manifest_path="dataset_manifest.json", output_dir="data/raw_youtube"):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    for item in manifest:
        video_id = item['video_id']
        url = item['url']
        channel_id = item['channel_id']
        domain = item['domain']
        lang = item['language']
        
        # Format: data/raw_youtube/CHANNELID_DOMAIN_LANG_VIDEOID.ext
        out_tmpl = os.path.join(output_dir, f"{channel_id}_{domain}_{lang}_{video_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_tmpl,
            'sleep_interval': 15,          # Anti-ban: Sleep between 15
            'max_sleep_interval': 30,      # and 30 seconds
            'ignoreerrors': True,          # Skip if video is private/deleted
            'quiet': False,
        }
        
        print(f"Downloading: {url} -> {out_tmpl}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            
        print("Sleeping to avoid rate limit...")
        time.sleep(random.uniform(5, 10)) # Extra safety padding

if __name__ == "__main__":
    scrape_audio()
```

- [ ] **Step 2: Commit**

```bash
git add arti6_linearvc_demo/scrape_vtuber_audio.py
git commit -m "feat: implement rate-limited youtube audio scraper"
```

---

### Task 3: Implement the Purifier / Source Separation (`purify_audio.py` - Part 1)

**Files:**
- Create: `arti6_linearvc_demo/purify_audio.py`

- [ ] **Step 1: Write the Demucs separation logic**

Create `arti6_linearvc_demo/purify_audio.py`. This script will iterate over files in `data/raw_youtube` and call `demucs` via `subprocess` to extract the `vocals.wav` track into a `separated` directory.

```python
import os
import glob
import subprocess
import shutil

def run_source_separation(input_dir="data/raw_youtube", output_dir="data/separated"):
    os.makedirs(output_dir, exist_ok=True)
    
    audio_files = glob.glob(os.path.join(input_dir, "*.*"))
    for file_path in audio_files:
        filename = os.path.basename(file_path)
        base_name, _ = os.path.splitext(filename)
        
        # Demucs output structure: output_dir/htdemucs/base_name/vocals.wav
        expected_vocal_path = os.path.join(output_dir, "htdemucs", base_name, "vocals.wav")
        final_vocal_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
        
        if os.path.exists(final_vocal_path):
            print(f"Skipping {filename}, already separated.")
            continue
            
        print(f"Running Demucs on {filename}...")
        cmd = [
            "demucs",
            "--two-stems=vocals",  # Only extract vocals to save time
            "-o", output_dir,
            file_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            # Move the vocal file up and clean up
            if os.path.exists(expected_vocal_path):
                shutil.move(expected_vocal_path, final_vocal_path)
                shutil.rmtree(os.path.join(output_dir, "htdemucs", base_name))
        except subprocess.CalledProcessError as e:
            print(f"Demucs failed for {filename}: {e}")

if __name__ == "__main__":
    run_source_separation()
```

- [ ] **Step 2: Commit**

```bash
git add arti6_linearvc_demo/purify_audio.py
git commit -m "feat: add demucs vocal separation to purifier"
```

---

### Task 4: Implement VAD Chunking (`purify_audio.py` - Part 2)

**Files:**
- Modify: `arti6_linearvc_demo/purify_audio.py`

- [ ] **Step 1: Add Silero VAD chunking logic**

Modify `purify_audio.py` to add `chunk_vocals_with_vad` function using `torchaudio` and Silero VAD. Update the main block to run both steps.

```python
import os
import glob
import subprocess
import shutil
import torch
import torchaudio

def run_source_separation(input_dir="data/raw_youtube", output_dir="data/separated"):
    # ... [Keep existing code exactly as written in Task 3] ...
    os.makedirs(output_dir, exist_ok=True)
    audio_files = glob.glob(os.path.join(input_dir, "*.*"))
    for file_path in audio_files:
        filename = os.path.basename(file_path)
        base_name, _ = os.path.splitext(filename)
        expected_vocal_path = os.path.join(output_dir, "htdemucs", base_name, "vocals.wav")
        final_vocal_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
        if os.path.exists(final_vocal_path):
            print(f"Skipping {filename}, already separated.")
            continue
        print(f"Running Demucs on {filename}...")
        cmd = ["demucs", "--two-stems=vocals", "-o", output_dir, file_path]
        try:
            subprocess.run(cmd, check=True)
            if os.path.exists(expected_vocal_path):
                shutil.move(expected_vocal_path, final_vocal_path)
                shutil.rmtree(os.path.join(output_dir, "htdemucs", base_name))
        except subprocess.CalledProcessError as e:
            print(f"Demucs failed for {filename}: {e}")

def chunk_vocals_with_vad(input_dir="data/separated", output_dir="data/chunks"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading Silero VAD model...")
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=False,
                                  trust_repo=True)
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
    
    vocal_files = glob.glob(os.path.join(input_dir, "*_vocals.wav"))
    for file_path in vocal_files:
        filename = os.path.basename(file_path)
        base_name = filename.replace("_vocals.wav", "")
        
        print(f"Chunking {filename}...")
        # Silero VAD works best at 16kHz
        wav = read_audio(file_path, sampling_rate=16000)
        
        # Get timestamps (returns list of dicts with 'start' and 'end' in samples)
        speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)
        
        for i, ts in enumerate(speech_timestamps):
            start = ts['start']
            end = ts['end']
            duration_sec = (end - start) / 16000.0
            
            # Filter out chunks that are too short (< 2s) or too long (> 15s)
            if 2.0 <= duration_sec <= 15.0:
                chunk = wav[start:end]
                # Format: output_dir/CHANNEL_DOMAIN_LANG_VIDEOID_chunk001.wav
                out_path = os.path.join(output_dir, f"{base_name}_chunk{i:03d}.wav")
                save_audio(out_path, chunk, sampling_rate=16000)

if __name__ == "__main__":
    print("--- Step 1: Source Separation ---")
    run_source_separation()
    print("--- Step 2: VAD Chunking ---")
    chunk_vocals_with_vad()
```

- [ ] **Step 2: Commit**

```bash
git add arti6_linearvc_demo/purify_audio.py
git commit -m "feat: add silero vad chunking logic to purifier"
```
