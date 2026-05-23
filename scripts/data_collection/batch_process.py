import os
import glob
import json
import traceback
from isolate_vocals import isolate
from classify_audio import classify

def process_batch(input_dir, output_dir):
    demucs_out = os.path.join(output_dir, "demucs_tmp")
    final_dir = os.path.join(output_dir, "vtuber_clean")
    os.makedirs(demucs_out, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)
    
    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory {input_dir} not found.")
        return

    # Find all wavs in the raw folder
    wav_files = glob.glob(os.path.join(input_dir, "**", "*.wav"), recursive=True)
    print(f"Found {len(wav_files)} WAV files to process.")

    results = []
    
    for i, file_path in enumerate(wav_files):
        print(f"[{i+1}/{len(wav_files)}] Processing {file_path}...")
        try:
            base_name = os.path.basename(file_path)
            
            # Step 1: Isolate Vocals
            print("  -> Isolating vocals...")
            vocals_path = isolate(file_path, demucs_out)
            
            # Step 2: Classify
            print("  -> Classifying audio...")
            info = classify(vocals_path)
            
            # Step 3: Save to clean dir
            clean_path = os.path.join(final_dir, f"clean_{base_name}")
            import shutil
            shutil.copy(vocals_path, clean_path)
            
            # Record result
            res = {
                "original_file": file_path,
                "clean_file": clean_path,
                "classification": info
            }
            results.append(res)
            
            print(f"  -> Success. Language: {info.get('language')}")
            
        except Exception as e:
            print(f"  -> Failed: {e}")
            traceback.print_exc()

    # Save summary
    summary_file = os.path.join(final_dir, "batch_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Batch processing complete. Summary saved to {summary_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw_audio", help="Input directory of raw WAV files")
    parser.add_argument("--output", default="data", help="Output directory base")
    args = parser.parse_args()
    
    process_batch(args.input, args.output)
