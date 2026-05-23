import os
import glob
from pydub import AudioSegment
from pydub.silence import split_on_silence
import json

def remove_silence(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    wav_files = glob.glob(os.path.join(input_dir, "clean_*.wav"))
    
    print(f"Found {len(wav_files)} files to trim.")
    
    # Copy over the batch_summary if it exists so we don't lose it
    summary_path = os.path.join(input_dir, "batch_summary.json")
    if os.path.exists(summary_path):
        import shutil
        shutil.copy(summary_path, os.path.join(output_dir, "batch_summary.json"))

    for i, file_path in enumerate(wav_files):
        base_name = os.path.basename(file_path)
        out_path = os.path.join(output_dir, base_name)
        
        print(f"[{i+1}/{len(wav_files)}] Trimming {base_name}...")
        try:
            audio = AudioSegment.from_wav(file_path)
            
            # Split on silence:
            # - min_silence_len = 1000ms (1 sec of silence triggers a split)
            # - silence_thresh = -45 dBFS (what counts as silence)
            # - keep_silence = 200ms (leave 0.2s of silence at the ends of chunks for natural pacing)
            chunks = split_on_silence(
                audio, 
                min_silence_len=1000,
                silence_thresh=-45,
                keep_silence=200
            )
            
            if len(chunks) > 0:
                trimmed_audio = chunks[0]
                for chunk in chunks[1:]:
                    trimmed_audio += chunk
                
                trimmed_audio.export(out_path, format="wav")
                
                # Calculate how much was removed
                orig_sec = len(audio) / 1000.0
                new_sec = len(trimmed_audio) / 1000.0
                print(f"  -> Saved to {out_path} (Reduced from {orig_sec:.1f}s to {new_sec:.1f}s)")
            else:
                print(f"  -> No audio detected above threshold in {base_name}, copying original.")
                audio.export(out_path, format="wav")
                
        except Exception as e:
            print(f"  -> Failed: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/vtuber_clean", help="Input directory")
    parser.add_argument("--output", default="data/vtuber_trimmed", help="Output directory")
    args = parser.parse_args()
    
    remove_silence(args.input, args.output)
