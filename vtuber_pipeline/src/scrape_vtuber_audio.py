import argparse
import json
import logging
import os
import sys
import subprocess

def setup_logger(verbose: bool) -> logging.Logger:
    """Set up basic structured logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("scrape_vtuber")

def load_manifest(manifest_path: str) -> dict:
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_manifest(manifest: dict, manifest_path: str) -> None:
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="VTuber Audio Scraper using Standalone yt-dlp")
    parser.add_argument("urls", nargs="*", help="YouTube Channel or Video URLs")
    parser.add_argument("--input-manifest", help="Path to a discovery manifest JSON to download from")
    parser.add_argument("--tags", nargs="*", default=[], help="Target tags (e.g. Speech, Singing, EN, JP)")
    parser.add_argument("--output-dir", default="data/raw_audio", help="Output directory for audio files")
    parser.add_argument("--manifest", help="Path to manifest JSON (default: <output-dir>/manifest.json)")
    parser.add_argument("--sleep-requests", type=float, default=15.0, help="Sleep seconds between HTTP requests (Anti-ban)")
    parser.add_argument("--sleep-interval", type=int, default=15, help="Minimum sleep seconds between downloads")
    parser.add_argument("--max-sleep-interval", type=int, default=30, help="Maximum sleep seconds between downloads")
    parser.add_argument("--cookiefile", default="cookies_netscape.txt", help="Path to Netscape cookies file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--max-download-duration", type=float, default=1800.0, help="If a video duration exceeds this in seconds, only download the first max-download-duration seconds. Set to 0 to disable.")
    
    args = parser.parse_args()
    logger = setup_logger(args.verbose)

    os.makedirs(args.output_dir, exist_ok=True)
    manifest_path = args.manifest or os.path.join(args.output_dir, "manifest.json")
    manifest = load_manifest(manifest_path)
    
    download_targets = []
    
    if args.input_manifest:
        try:
            with open(args.input_manifest, 'r', encoding='utf-8') as f:
                discovery_data = json.load(f)
                if isinstance(discovery_data, dict):
                    for vid, vdata in discovery_data.items():
                        download_targets.append({
                            'url': vdata.get('url', f"https://www.youtube.com/watch?v={vid}"),
                            'tags': vdata.get('tags', args.tags),
                            'domain': vdata.get('domain', "Unknown")
                        })
                elif isinstance(discovery_data, list):
                    for vdata in discovery_data:
                        download_targets.append({
                            'url': vdata.get('url'),
                            'tags': vdata.get('tags', args.tags),
                            'domain': vdata.get('domain', "Unknown")
                        })
        except Exception as e:
            logger.error(f"Failed to load input manifest: {e}")
            sys.exit(1)
            
    for url in args.urls:
        domain = "Unknown"
        if "Speech" in args.tags:
            domain = "Speech"
        elif "Singing" in args.tags:
            domain = "Singing"
        elif args.tags:
            domain = args.tags[0]
        download_targets.append({
            'url': url,
            'tags': args.tags,
            'domain': domain
        })

    if not download_targets:
        logger.error("No URLs provided via CLI arguments or --input-manifest")
        sys.exit(1)

    # Use project bin/yt-dlp binary if it exists
    yt_dlp_bin = "bin/yt-dlp"
    if not os.path.exists(yt_dlp_bin):
        yt_dlp_bin = "yt-dlp"
        
    logger.info(f"Using yt-dlp binary at: {yt_dlp_bin}")
    logger.info(f"Starting download for {len(download_targets)} target(s)")

    for target in download_targets:
        url = target['url']
        domain = target['domain']
        tags = target['tags']
        logger.info(f"Processing URL: {url} (Domain: {domain})")
        try:
            # Stage 1: Extract info using subprocess
            cmd_info = [
                yt_dlp_bin,
                "--dump-single-json",
                "--no-playlist",
            ]
            if os.path.exists(args.cookiefile):
                cmd_info.extend(["--cookiefile", args.cookiefile])
                
            cmd_info.append(url)
            
            logger.info(f"Extracting metadata command: {' '.join(cmd_info)}")
            res = subprocess.run(cmd_info, capture_output=True, text=True, encoding='utf-8')
            if res.returncode != 0:
                logger.warning(f"Failed to extract info for {url}: {res.stderr.strip()}")
                continue
                
            try:
                info = json.loads(res.stdout)
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse JSON for {url}: {je}")
                continue
                
            if not info:
                logger.warning(f"No info returned for {url}")
                continue
                
            # If the extraction returned a playlist, handle it or get first entry
            entries = info.get('entries', [info])
            
            for entry in entries:
                if not entry:
                    continue
                video_id = entry.get('id')
                if not video_id:
                    continue
                    
                duration = entry.get('duration')
                uploader_id = entry.get('channel_id') or entry.get('uploader_id') or 'unknown'
                uploader = entry.get('uploader')
                upload_date = entry.get('upload_date')
                title = entry.get('title')
                webpage_url = entry.get('webpage_url', f"https://www.youtube.com/watch?v={video_id}")
                
                # Check if file already exists in manifest and output directory
                filename = f"{uploader_id}_{video_id}.m4a"
                dest_path = os.path.join(args.output_dir, filename)
                
                if os.path.exists(dest_path) and video_id in manifest:
                    logger.info(f"File {filename} already exists. Skipping download.")
                    continue
                
                download_sections = None
                if args.max_download_duration > 0 and duration and duration > args.max_download_duration:
                    logger.info(f"Video {video_id} duration ({duration}s) exceeds --max-download-duration ({args.max_download_duration}s). Only downloading first {args.max_download_duration}s.")
                    download_sections = f"*0-{int(args.max_download_duration)}"
                
                # Stage 2: Perform actual download
                out_tmpl = os.path.join(args.output_dir, f"{uploader_id}_{video_id}.%(ext)s")
                cmd_dl = [
                    yt_dlp_bin,
                    "-x",
                    "--audio-format", "m4a",
                    "--audio-quality", "192",
                    "--no-playlist",
                    "-o", out_tmpl,
                    "--sleep-interval", str(args.sleep_interval),
                    "--max-sleep-interval", str(args.max_sleep_interval),
                    "--sleep-requests", str(args.sleep_requests),
                ]
                
                if os.path.exists(args.cookiefile):
                    cmd_dl.extend(["--cookiefile", args.cookiefile])
                    
                if download_sections:
                    cmd_dl.extend(["--download-sections", download_sections])
                    
                cmd_dl.append(webpage_url)
                
                logger.info(f"Running download command: {' '.join(cmd_dl)}")
                dl_res = subprocess.run(cmd_dl, capture_output=True, text=True, encoding='utf-8')
                
                if dl_res.returncode != 0:
                    logger.error(f"Download failed for {webpage_url}: {dl_res.stderr.strip()}")
                    # If download failed but file was partially downloaded/converted or if it was exit code 1 due to section downloading,
                    # check if the destination file actually exists
                    if not os.path.exists(dest_path):
                        continue
                
                manifest[video_id] = {
                    'video_id': video_id,
                    'channel_id': uploader_id,
                    'uploader': uploader,
                    'upload_date': upload_date,
                    'title': title,
                    'duration': duration,
                    'tags': tags,
                    'domain': domain,
                    'filename': filename,
                    'url': webpage_url
                }
                
                save_manifest(manifest, manifest_path)
                logger.info(f"Saved metadata for video {video_id}")
                
        except Exception as e:
            logger.error(f"Error processing {url}: {e}", exc_info=args.verbose)

    logger.info("Scraping completed.")

if __name__ == "__main__":
    main()
