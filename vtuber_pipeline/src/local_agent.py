#!/usr/bin/env python3
"""
VTuber Data Agent Orchestrator

This script serves as the primary entry point for the automated VTuber data pipeline.
It orchestrates a multi-step data engineering process:
1. Discovery: Analyzes a YouTube channel using Gemini to isolate Speech vs Singing content.
2. Download: Fetches raw audio tracks using yt-dlp.
3. Purify & Segment: Uses Demucs to strip background music and Silero VAD to segment 
   audio into pristine, phonetic chunks suitable for voice conversion ML training.
4. Archive & Upload: (Optional) Packages the dataset and SCPs it to a remote training server.

Usage:
    python local_agent.py "https://www.youtube.com/@Channel" --max-videos 20
"""

import argparse
import logging
import os
import subprocess
import sys
import tarfile
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None):
    """Utility to run a subprocess command with logging."""
    cmd_str = " ".join(cmd)
    logger.info(f"Executing: {cmd_str}")
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {cmd_str}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="End-to-end Local VTuber Data Agent Orchestrator")
    parser.add_argument("channel_url", help="YouTube Channel URL (e.g., https://www.youtube.com/@EnnaAlouette)")
    parser.add_argument("--max-videos", type=int, default=10, help="Max videos to check in discovery")
    parser.add_argument("--workspace", default="data", help="Local directory to store intermediate and final data")
    
    args = parser.parse_args()
    
    # 1. Verification of environment
    if not os.environ.get("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable is missing. It is required for the Discovery Agent.")
        sys.exit(1)
        
    upload_ip = os.environ.get("UPLOAD_SERVER_IP")
    upload_user = os.environ.get("UPLOAD_SERVER_USER")
    upload_path = os.environ.get("UPLOAD_SERVER_PATH")
    
    if not all([upload_ip, upload_user, upload_path]):
        logger.warning("Upload environment variables missing (UPLOAD_SERVER_IP, UPLOAD_SERVER_USER, UPLOAD_SERVER_PATH).")
        logger.warning("The script will run the pipeline but SKIP the final server upload.")
        do_upload = False
    else:
        do_upload = True

    # 2. Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(base_dir, "src")
    
    workspace = os.path.abspath(args.workspace)
    os.makedirs(workspace, exist_ok=True)
    
    raw_dir = os.path.join(workspace, "raw_audio")
    clean_dir = os.path.join(workspace, "vtuber_clean")
    manifest_path = os.path.join(workspace, "discovery_manifest.json")
    
    # Extract a friendly channel name for the tarball
    channel_slug = args.channel_url.strip('/').split('/')[-1].replace('@', '')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"dataset_{channel_slug}_{timestamp}.tar.gz"
    archive_path = os.path.join(workspace, archive_name)
    
    # Step 1: Discovery
    logger.info("========== STEP 1: DISCOVERY ==========")
    cmd_discover = [
        sys.executable, os.path.join(src_dir, "discover_videos.py"),
        args.channel_url,
        "--max-videos", str(args.max_videos),
        "--output", manifest_path
    ]
    run_command(cmd_discover)
    
    # Step 2: Download
    logger.info("========== STEP 2: DOWNLOAD ==========")
    cookie_path = os.path.join(base_dir, "cookies_netscape.txt")
    cmd_download = [
        sys.executable, os.path.join(src_dir, "scrape_vtuber_audio.py"),
        "--input-manifest", manifest_path,
        "--output-dir", raw_dir
    ]
    if os.path.exists(cookie_path):
        cmd_download.extend(["--cookiefile", cookie_path])
    else:
        logger.warning(f"No cookie file found at {cookie_path}. Age restricted videos may fail.")
    run_command(cmd_download)
    
    # Step 3: Purify & Segment
    logger.info("========== STEP 3: PURIFY & SEGMENT ==========")
    cmd_purify = [
        sys.executable, os.path.join(src_dir, "purify_audio.py"),
        "--manifest", os.path.join(raw_dir, "manifest.json"),
        "--input-dir", raw_dir,
        "--output-dir", clean_dir
    ]
    run_command(cmd_purify)
    
    # Step 4: Archive
    logger.info("========== STEP 4: ARCHIVE ==========")
    logger.info(f"Compressing {clean_dir} into {archive_path}...")
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(clean_dir, arcname=os.path.basename(clean_dir))
        logger.info("Archive created successfully.")
    except Exception as e:
        logger.error(f"Failed to create archive: {e}")
        sys.exit(1)
        
    # Step 5: Upload
    logger.info("========== STEP 5: UPLOAD ==========")
    if do_upload:
        target = f"{upload_user}@{upload_ip}:{upload_path}"
        logger.info(f"Uploading {archive_name} to {target} via SCP...")
        cmd_upload = ["scp", archive_path, target]
        run_command(cmd_upload)
        logger.info("Upload complete!")
    else:
        logger.info(f"Skipping upload. Your processed dataset is ready at: {archive_path}")

    logger.info("Pipeline Execution Finished Successfully.")

if __name__ == "__main__":
    main()
