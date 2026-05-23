# brainstorm: VTuber Local Orchestrator & Uploader

## Goal

Create an overarching "run-all" orchestrator script/agent that the user can execute on their local machine. This script will chain together the previously built tools (discovery -> scraping -> purifying -> segmenting). Once the data processing is complete, the script will automatically compress the final dataset (`data/vtuber_clean`) into an archive (e.g., `.zip` or `.tar.gz`) and upload it to a remote server.

## What I already know

*   The user wants to run the discovery, downloading, and purifying steps locally (likely due to bandwidth or IP ban risks on the server).
*   The individual scripts (`discover_videos.py`, `scrape_vtuber_audio.py`, `purify_audio.py`) are fully built and tested in `vtuber_pipeline/src/`.
*   The user wants this to be packaged so they just download the repository/scripts, and run one single "Agent"/script locally.
*   After the local processing completes, the results need to be uploaded to a server automatically.

## Assumptions (temporary)

*   The target channel or list of channels will be provided as input to this master script.
*   The upload will use a standard protocol like `scp`, `rsync`, or an S3 compatible CLI, depending on the user's server setup.

## Open Questions

*   All open questions resolved.

## Requirements

*   Provide a master entrypoint `vtuber_pipeline/src/local_agent.py` that takes a YouTube channel URL.
*   Step 1: Execute `discover_videos.py` to get the manifest.
*   Step 2: Execute `scrape_vtuber_audio.py` using that manifest.
*   Step 3: Execute `purify_audio.py` to get clean chunks.
*   Step 4: Compress `data/vtuber_clean` into `dataset_<channel_id>.tar.gz`.
*   Step 5: Upload the archive to a remote server. The agent will use `scp` or `rsync` by default, driven by environment variables (`UPLOAD_SERVER_IP`, `UPLOAD_SERVER_USER`, `UPLOAD_SERVER_PATH`).

## Decision (ADR-lite)

**Context**: The user wants an end-to-end automated local agent that finishes by uploading to a server. They left the specific protocol decision to the AI.
**Decision**: We will implement a Python-based orchestrator (`local_agent.py`) that uses `subprocess` to chain the existing CLI tools. For the upload, it will compress the results and use `scp` (or `rsync`), configured entirely via environment variables. This is the most universal and dependency-free method for Linux/Mac/WSL users to push files to an AI dev server.

## Acceptance Criteria (evolving)

*   [ ] A single script exists that successfully strings together all 5 steps without manual intervention.

## Out of Scope (explicit)

*   Rewriting the core scraping logic (already handled).