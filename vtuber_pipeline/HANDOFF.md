# Codex Local Agent Handoff: VTuber Dataset Collection

This document is the high-level prompt and specification for the local agent (**Codex**) to execute the data collection pipeline.

## 1. Research Goal (The Demand)
We are collecting a high-quality dataset of VTuber audio to research **Voice Conversion (VC)**, specifically focusing on cross-domain identity robustness (Speech vs. Singing) and multilingual capabilities (English/Japanese).

### Quality Requirements:
*   **Target Channels**: Focus on multilingual VTubers (e.g., Enna Alouette, FuwaMoco).
*   **Speech Domain**: Solo Zatsudan (Chatting) streams. Must be clear, solo, and high-fidelity.
*   **Singing Domain**: Karaoke/MV streams. Must be multilingual (EN/JP) where possible.
*   **Solo vs. Group**:
    *   For solo VTubers (Enna, etc.): Avoid collabs or group streams to prevent voice overlap.
    *   **Special Case (FuwaMoco/Twins)**: Accept their streams despite the inherent overlap. This data is valuable for chorus separation and twin-identity research.
*   **Voice Style**: Prefer VTubers with distinct habits (e.g., FuwaMoco's frequent fillers and unique pronunciation).

## 2. Available Local Tools
The following scripts are provided in the `src/` directory:
1.  `discover_videos.py`: Uses `yt-dlp` and Gemini API to dynamically categorize a channel's videos into `Speech`, `Singing`, or `Collab`.
2.  `scrape_vtuber_audio.py`: Downloads audio and generates a metadata manifest.
3.  `purify_audio.py`: Runs Demucs (BGM removal) and Silero VAD (intelligent slicing into 3-15s chunks).
4.  `local_agent.py`: A master orchestrator that chains these steps.

## 3. Codex Execution Instructions
As the local agent, you are tasked with:
1.  **Dynamic Discovery**: Decide which videos to download based on the requirements above. You can run `discover_videos.py` to get a list, or manually inspect a channel's recent uploads using `yt-dlp`.
2.  **Execution & Debugging**: Run the collection pipeline. If a script fails due to local environment issues (missing dependencies, path errors), you are authorized to debug and fix the code.
3.  **Data Packaging**: Once the `data/vtuber_clean` folder is populated with chunks, compress the directory into a `.tar.gz` archive.
4.  **Automated Upload**: Transfer the final archive back to the server. You can use `scp` or `rsync` using the following environment variables if provided:
    *   `UPLOAD_SERVER_IP`, `UPLOAD_SERVER_USER`, `UPLOAD_SERVER_PATH`.

## 4. Environment Checklist
*   Ensure `yt-dlp`, `ffmpeg`, `torch`, `torchaudio`, and `google-genai` are installed.
*   Use `cookies_netscape.txt` for YouTube access if available.
