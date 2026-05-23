import os
import argparse
from scrape_youtube import download_audio
from isolate_vocals import isolate
from classify_audio import classify
import shutil

def main(urls, output_dir):
    raw_dir = os.path.join(output_dir, "raw")
    demucs_out = os.path.join(output_dir, "demucs_tmp")
    final_dir = os.path.join(output_dir, "vtuber_clean")
    os.makedirs(final_dir, exist_ok=True)
    
    for url in urls:
        print(f"Processing URL: {url}")
        
        try:
            if os.path.isfile(url):
                print(f"Local file detected: {url}")
                raw_path = os.path.join(raw_dir, os.path.basename(url))
                os.makedirs(raw_dir, exist_ok=True)
                shutil.copy(url, raw_path)
                print(f"Copied to {raw_path}")
            else:
                print("Downloading...")
                raw_path = download_audio(url, raw_dir)
                print(f"Downloaded to {raw_path}")
                
            print("Isolating vocals...")
            vocals_path = isolate(raw_path, demucs_out)
            print(f"Vocals isolated at {vocals_path}")
            
            print("Classifying audio...")
            info = classify(vocals_path)
            print(f"Classification info: {info}")
            
            final_path = os.path.join(final_dir, os.path.basename(vocals_path))
            shutil.copy(vocals_path, final_path)
            print(f"Saved clean vocals to {final_path}")
            
        except Exception as e:
            print(f"Failed to process {url}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="+", required=True)
    parser.add_argument("--out", default="data")
    args = parser.parse_args()
    main(args.urls, args.out)
