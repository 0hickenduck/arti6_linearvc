#!/usr/bin/env python3
import yt_dlp
import os
import argparse
import json
import tarfile
import logging
from pathlib import Path
from datetime import timedelta, datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('downloader.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
IDENTITIES = ["Enna", "Kiara", "Mori", "FuwaMoco", "Baelz"]
SINGING_KEYWORDS = [
    "MV", "Cover", "Original Song", "Singing", "Karaoke", "歌枠", "歌ってみた", 
    "Original MV", "Music Video", "Setlist", "Sing", "Song"
]
TALKING_KEYWORDS = [
    "Chatting", "Zatsudan", "ASMR", "Talk", "雑談", "Free Talk", "Reading",
    "Stream", "Live", "Gaming", "Collab", "Review"
]

class PolyglotDownloader:
    def __init__(self, browser='chrome', output_root='raw_audio'):
        self.browser = browser
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.output_root / "download_stats.json"
        self.stats = self._load_stats()

    def _load_stats(self):
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode {self.stats_file}, starting fresh.")
                return {}
        return {}

    def _save_stats(self):
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def determine_type(self, title):
        title_lower = title.lower()
        for kw in SINGING_KEYWORDS:
            if kw.lower() in title_lower:
                return "Singing"
        for kw in TALKING_KEYWORDS:
            if kw.lower() in title_lower:
                return "Talking"
        # Default to Talking as it's more common for long streams
        return "Talking"

    def download_url(self, url, identity, language='EN', playlist_items=None):
        ydl_opts = {
            'format': 'ba/ba*',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',
            'logger': logger,
            'remote_components': ['ejs:github'],
        }
        
        if playlist_items:
            ydl_opts['playlist_items'] = playlist_items
        
        if self.browser:
            ydl_opts['cookiesfrombrowser'] = (self.browser,)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Extracting info for {url}...")
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                if self.browser:
                    logger.warning(f"Failed with cookies, retrying without: {e}")
                    ydl_opts.pop('cookiesfrombrowser')
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_no_cookies:
                        try:
                            info = ydl_no_cookies.extract_info(url, download=False)
                        except Exception as e2:
                            logger.error(f"Error extracting info for {url}: {e2}")
                            return
                else:
                    logger.error(f"Error extracting info for {url}: {e}")
                    return

            if not info:
                logger.warning(f"No info found for {url}")
                return

            # Handle both single video and playlist
            entries = info.get('entries', [info])
            
            for entry in entries:
                if not entry: continue
                
                title = entry.get('title', 'Unknown Title')
                duration = entry.get('duration', 0)
                video_id = entry.get('id')
                webpage_url = entry.get('webpage_url')
                
                if not video_id:
                    continue

                v_type = self.determine_type(title)
                dest_dir = self.output_root / identity / f"{language}_{v_type}"
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                output_path = dest_dir / f"{video_id}.wav"
                
                # Check if already downloaded
                if identity in self.stats and video_id in self.stats[identity].get('videos', []):
                    if output_path.exists():
                        logger.info(f"Skipping {video_id} - already downloaded.")
                        continue

                logger.info(f"Processing: {title} (ID: {video_id})")
                logger.info(f"Identity: {identity}, Lang: {language}, Type: {v_type}, Duration: {timedelta(seconds=duration)}")
                
                # Use a fresh downloader for the actual download to avoid parameter pollution
                download_opts = ydl_opts.copy()
                download_opts['outtmpl'] = str(dest_dir / f"%(id)s.%(ext)s")
                
                try:
                    with yt_dlp.YoutubeDL(download_opts) as ydl_down:
                        ydl_down.download([webpage_url])
                except Exception as e:
                    logger.error(f"Failed to download {webpage_url}: {e}")
                    continue
                
                if not output_path.exists():
                    logger.warning(f"Expected {output_path} not found after download.")
                    continue
                
                # Update stats
                if identity not in self.stats:
                    self.stats[identity] = {'total_duration': 0, 'videos': []}
                
                if video_id not in self.stats[identity]['videos']:
                    self.stats[identity]['total_duration'] += duration
                    self.stats[identity]['videos'].append(video_id)
                    self._save_stats()
                
                total_dur_str = str(timedelta(seconds=self.stats[identity]['total_duration']))
                logger.info(f"Success! Total collected for {identity}: {total_dur_str}")

    def package(self):
        tar_name = "polyglot_raw_audio.tar.gz"
        logger.info(f"Packaging {self.output_root} into {tar_name}...")
        
        # Calculate stats for the readme
        stats_summary = ""
        total_overall = 0
        for identity, data in self.stats.items():
            dur = data['total_duration']
            total_overall += dur
            dur_str = str(timedelta(seconds=dur))
            stats_summary += f"- **{identity}**: {dur_str} total audio collected.\n"

        if not stats_summary:
            stats_summary = "No data collected yet.\n"
        else:
            stats_summary += f"- **TOTAL**: {str(timedelta(seconds=total_overall))}\n"

        # Create Tar
        try:
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(self.output_root, arcname=os.path.basename(self.output_root))
        except Exception as e:
            logger.error(f"Error creating tarball: {e}")
            return
        
        instructions = f"""# Transfer Instructions

1. Upload `{tar_name}` to the lab server.
2. Extract it: `tar -xzf {tar_name}`.
3. Move the `raw_audio/` folder to your project data directory:
   `mv raw_audio/ path/to/arti6_linearvc/data/`
4. Run the isolation and classification pipeline on the lab server.

## Collection Summary
{stats_summary}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        try:
            with open("transfer_instructions.md", "w") as f:
                f.write(instructions)
            logger.info("Packaging complete.")
            logger.info(f"Files to transfer: {tar_name}, transfer_instructions.md")
        except Exception as e:
            logger.error(f"Failed to write transfer_instructions.md: {e}")

def main():
    parser = argparse.ArgumentParser(description="Polyglot Dataset Downloader")
    parser.add_argument("--url", help="YouTube URL, Playlist URL, or path to a text file with URLs")
    parser.add_argument("--identity", choices=IDENTITIES, help=f"Identity name (Required for download). Choices: {', '.join(IDENTITIES)}")
    parser.add_argument("--lang", default="EN", help="Language code (e.g., EN, JP, DE). Default: EN")
    parser.add_argument("--browser", default="chrome", help="Browser for cookies (chrome, edge, firefox, safari). Default: chrome")
    parser.add_argument("--package", action="store_true", help="Package the raw_audio folder and exit")
    parser.add_argument("--playlist-items", help="Playlist items to download (e.g., 1-10)")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    downloader = PolyglotDownloader(browser=args.browser)

    if args.package:
        downloader.package()
        return

    if not args.url or not args.identity:
        logger.error("--url and --identity are required for downloading.")
        sys.exit(1)

    # Check if url is a file
    urls = []
    if os.path.isfile(args.url):
        logger.info(f"Reading URLs from file: {args.url}")
        try:
            with open(args.url, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            logger.error(f"Error reading file {args.url}: {e}")
            sys.exit(1)
    else:
        urls = [args.url]

    for url in urls:
        downloader.download_url(url, args.identity, args.lang, args.playlist_items)

if __name__ == "__main__":
    main()
