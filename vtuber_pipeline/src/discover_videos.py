import argparse
import json
import logging
import os
import sys
from typing import List, Dict, Any

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field
except ImportError:
    genai = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoClassification(BaseModel):
    video_id: str = Field(description="The YouTube video ID")
    domain: str = Field(description="One of: 'Speech', 'Singing', 'Collab', 'Gaming', or 'Ignore'")
    reason: str = Field(description="Brief reason for this classification")

class BatchClassificationResult(BaseModel):
    classifications: List[VideoClassification]

def fetch_recent_videos(channel_url: str, max_downloads: int = 50) -> List[Dict[str, Any]]:
    """Use yt-dlp to extract flat playlist metadata from a channel."""
    if not yt_dlp:
        logger.error("yt-dlp is not installed. Run: pip install yt-dlp")
        sys.exit(1)

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'playlistend': max_downloads,
    }
    
    videos = []
    logger.info(f"Fetching up to {max_downloads} recent videos from {channel_url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        videos.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': entry.get('url', f"https://www.youtube.com/watch?v={entry.get('id')}"),
                            'channel_id': entry.get('channel_id') or info.get('id')
                        })
            else:
                # Single video
                videos.append({
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'url': info.get('webpage_url'),
                    'channel_id': info.get('channel_id')
                })
        except Exception as e:
            logger.error(f"Failed to fetch videos: {e}")
            
    logger.info(f"Fetched {len(videos)} videos.")
    return videos

def classify_videos_with_llm(videos: List[Dict[str, Any]], api_key: str) -> Dict[str, str]:
    """Use Gemini Flash to classify video titles into domains."""
    if not genai:
        logger.error("google-genai is not installed. Run: pip install google-genai pydantic")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    
    prompt = "You are an expert VTuber archivist classifying video titles for a voice cloning dataset.\n"
    prompt += "Classify each video into one of these Domains: 'Speech' (Zatsudan, Chatting, ASMR), 'Singing' (Karaoke, MV, Unplugged), 'Gaming', 'Collab', or 'Ignore'.\n\n"
    
    prompt += "CRITICAL RULES:\n"
    prompt += "1. We need pure solo audio. If the title indicates a collaboration with an external guest (e.g., 'ft.', 'w/', 'x', 'コラボ'), classify as 'Collab'.\n"
    prompt += "2. **FUWAMOCO / TWIN EXCEPTION**: If the channel is inherently a twin/group (like FuwaMoco), DO NOT classify their standard streams as 'Collab'. Treat their Zatsudan as 'Speech' and their Karaoke as 'Singing'. Only mark 'Collab' if a *third* person joins them.\n"
    prompt += "3. We want standard chatting (Zatsudan) for 'Speech'.\n\n"
    
    prompt += "Videos to classify:\n"
    for v in videos:
        prompt += f"ID: {v['id']} | Title: {v['title']}\n"

    logger.info("Sending batch to Gemini for classification...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BatchClassificationResult,
                temperature=0.1
            ),
        )
        
        result_json = response.text
        data = json.loads(result_json)
        
        domain_map = {}
        for item in data.get('classifications', []):
            domain_map[item['video_id']] = item['domain']
            logger.info(f"Classified [{item['video_id']}]: {item['domain']} (Reason: {item['reason']})")
            
        return domain_map
    except Exception as e:
        logger.error(f"LLM Classification failed: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Dynamically discover and categorize VTuber videos")
    parser.add_argument("channel_url", help="YouTube Channel URL (e.g., https://www.youtube.com/@FUWAMOCOch)")
    parser.add_argument("--max-videos", type=int, default=30, help="Max videos to check")
    parser.add_argument("--output", default="discovery_manifest.json", help="Output JSON path")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is required for LLM classification.")
        sys.exit(1)
        
    videos = fetch_recent_videos(args.channel_url, args.max_videos)
    if not videos:
        sys.exit(0)
        
    # Classify in batches of 50 to avoid prompt limits if we fetch too many
    domain_map = classify_videos_with_llm(videos, api_key)
    
    # Build final manifest compatible with our scraper
    manifest = {}
    for v in videos:
        vid = v['id']
        domain = domain_map.get(vid, "Unknown")
        
        # We only want to prep Speech and Singing for our extraction pipeline
        if domain in ["Speech", "Singing"]:
            manifest[vid] = {
                'video_id': vid,
                'channel_id': v['channel_id'],
                'title': v['title'],
                'url': v['url'],
                'domain': domain,
                'filename': f"{v['channel_id']}_{vid}.m4a", # Expected by scraper
                'tags': [domain]
            }
            
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Saved {len(manifest)} target videos to {args.output}")

if __name__ == "__main__":
    main()
