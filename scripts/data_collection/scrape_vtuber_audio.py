import argparse
import json
import logging
import os
import sys

# Try to import yt_dlp, gracefully handle missing dependency
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

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
    parser = argparse.ArgumentParser(description="VTuber Audio Scraper using yt-dlp")
    parser.add_argument("urls", nargs="+", help="YouTube Channel or Video URLs")
    parser.add_argument("--tags", nargs="*", default=[], help="Target tags (e.g. Speech, Singing, EN, JP)")
    parser.add_argument("--output-dir", default="data/raw_audio", help="Output directory for audio files")
    parser.add_argument("--manifest", help="Path to manifest JSON (default: <output-dir>/manifest.json)")
    parser.add_argument("--sleep-requests", type=float, default=15.0, help="Sleep seconds between HTTP requests (Anti-ban)")
    parser.add_argument("--sleep-interval", type=int, default=15, help="Minimum sleep seconds between downloads")
    parser.add_argument("--max-sleep-interval", type=int, default=30, help="Maximum sleep seconds between downloads")
    parser.add_argument("--cookiefile", default="cookies_netscape.txt", help="Path to Netscape cookies file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    logger = setup_logger(args.verbose)

    if yt_dlp is None:
        logger.error("yt-dlp is not installed. Please install it via 'pip install yt-dlp'")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)
    manifest_path = args.manifest or os.path.join(args.output_dir, "manifest.json")
    manifest = load_manifest(manifest_path)

    # Use uploader_id and video id for uniqueness and organization
    out_tmpl = os.path.join(args.output_dir, '%(uploader_id)s_%(id)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': out_tmpl,
        'sleep_interval': args.sleep_interval,
        'max_sleep_interval': args.max_sleep_interval,
        'sleep_requests': args.sleep_requests,
        'continuedl': True,  # Resume interrupted downloads
        'ignoreerrors': True, # Continue on download errors
        'extract_flat': False,
        'quiet': not args.verbose,
        'no_warnings': not args.verbose,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
        }],
    }

    if os.path.exists(args.cookiefile):
        ydl_opts['cookiefile'] = args.cookiefile
        logger.info(f"Using cookie file: {args.cookiefile}")
    else:
        logger.warning(f"Cookie file {args.cookiefile} not found. Age-restricted or member-only videos may fail.")

    logger.info(f"Starting download for {len(args.urls)} URL(s)")
    logger.info(f"Tags to apply: {args.tags}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in args.urls:
            logger.info(f"Processing URL: {url}")
            try:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    logger.warning(f"Failed to extract info for {url}")
                    continue
                
                entries = info.get('entries', [info])
                
                for entry in entries:
                    if not entry:
                        continue
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                        
                    uploader_id = entry.get('channel_id') or entry.get('uploader_id') or 'unknown'
                    # The out_tmpl generates {uploader_id}_{id}.{ext} and postprocessor forces m4a
                    filename = f"{uploader_id}_{video_id}.m4a"
                    
                    domain = "Unknown"
                    if "Speech" in args.tags:
                        domain = "Speech"
                    elif "Singing" in args.tags:
                        domain = "Singing"
                    elif args.tags:
                        domain = args.tags[0]
                        
                    manifest[video_id] = {
                        'video_id': video_id,
                        'channel_id': uploader_id,
                        'uploader': entry.get('uploader'),
                        'upload_date': entry.get('upload_date'),
                        'title': entry.get('title'),
                        'duration': entry.get('duration'),
                        'tags': args.tags,
                        'domain': domain,
                        'filename': filename,
                        'url': entry.get('webpage_url', f"https://www.youtube.com/watch?v={video_id}")
                    }
                    
                    # Interactively save manifest per item to prevent data loss
                    save_manifest(manifest, manifest_path)
                    logger.info(f"Saved metadata for video {video_id}")
                    
            except Exception as e:
                logger.error(f"Error processing {url}: {e}", exc_info=args.verbose)

    logger.info("Scraping completed.")

if __name__ == "__main__":
    main()
