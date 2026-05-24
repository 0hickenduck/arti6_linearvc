import os
import glob
import argparse
import logging
import traceback
from purify_audio import isolate_vocals, chunk_with_silero

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Process VTuber polyglot raw audio dataset")
    parser.add_argument("--input-dir", default="data/raw_audio", help="Directory containing raw audio files")
    parser.add_argument("--output-dir", default="data/vtuber_segmented", help="Directory for final chunked audio")
    parser.add_argument("--demucs-dir", default="data/temp_demucs", help="Temporary directory for Demucs output")
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    demucs_dir = os.path.abspath(args.demucs_dir)

    # find all wav files
    wav_files = glob.glob(os.path.join(input_dir, "**", "*.wav"), recursive=True)
    logger.info(f"Found {len(wav_files)} WAV files to process in {input_dir}")

    for idx, input_path in enumerate(wav_files):
        try:
            # We assume path structure: data/raw_audio/{Channel}/{Domain}/{video_id}.wav
            rel_path = os.path.relpath(input_path, input_dir)
            parts = rel_path.split(os.sep)
            
            if len(parts) >= 3:
                channel = parts[0]
                domain = parts[1]
                filename = parts[-1]
            elif len(parts) == 2:
                channel = parts[0]
                domain = "Unknown"
                filename = parts[1]
            else:
                channel = "Unknown"
                domain = "Unknown"
                filename = parts[-1]

            video_id = os.path.splitext(filename)[0]

            logger.info(f"[{idx+1}/{len(wav_files)}] Processing {video_id} ({domain}) for channel {channel}")

            # Step 1: Source Separation (Isolate Vocals)
            vocab_path = isolate_vocals(input_path, demucs_dir)
            
            # Step 2: VAD Slicing
            out_prefix_dir = os.path.join(output_dir, channel, domain)
            os.makedirs(out_prefix_dir, exist_ok=True)
            out_prefix = os.path.join(out_prefix_dir, video_id)
            
            chunks = chunk_with_silero(vocab_path, out_prefix)
            logger.info(f"Successfully generated {len(chunks)} chunks for {video_id}")
            
        except Exception as e:
            logger.error(f"Error processing {input_path}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
