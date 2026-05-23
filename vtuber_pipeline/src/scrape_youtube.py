import yt_dlp
import os

def download_audio(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    out_tmpl = os.path.join(output_dir, '%(id)s.%(ext)s')
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': out_tmpl,
        'quiet': True,
        'cookiefile': 'cookies_netscape.txt',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        expected_path = os.path.join(output_dir, f"{video_id}.wav")
        return expected_path
