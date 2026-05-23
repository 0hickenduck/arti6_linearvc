import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import traceback
from typing import List

import torch
import torchaudio

# Configure logging according to backend specs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def isolate_vocals(audio_path, output_dir):
    """
    Run HTDemucs to isolate vocals from the audio file.
    Follows project guidelines for error handling.
    """
    os.makedirs(output_dir, exist_ok=True)
    cmd = [sys.executable, '-m', 'demucs.separate', '-n', 'htdemucs', '--out', output_dir, audio_path]
    
    logger.info(f"Running demucs on {audio_path}")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Demucs failed for {audio_path}: {e.stderr}")
        raise RuntimeError(f"Demucs processing failed: {e}")

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    vocals_path = os.path.join(output_dir, 'htdemucs', base_name, 'vocals.wav')
    
    final_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
    if os.path.exists(vocals_path):
        shutil.copy(vocals_path, final_path)
    else:
        raise FileNotFoundError(f"Vocals not found at expected path: {vocals_path}")
        
    return final_path

def chunk_with_silero(wav_path: str, output_prefix: str, target_min_sec: int=3, target_max_sec: int=15) -> List[str]:
    """
    Use Silero VAD to slice the audio into clean, non-silent chunks.
    Stitches consecutive speech segments to reach a target duration.
    """
    try:
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                      model='silero_vad',
                                      force_reload=False,
                                      trust_repo=True)
    except TypeError:
        # Fallback for older PyTorch versions that don't support trust_repo
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                      model='silero_vad',
                                      force_reload=False)
    except Exception as e:
        logger.error(f"Failed to load Silero VAD model: {e}")
        raise

    get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks = utils
    
    SAMPLING_RATE = 16000
    try:
        wav = read_audio(wav_path, sampling_rate=SAMPLING_RATE)
    except Exception as e:
        logger.error(f"Failed to read audio {wav_path}: {e}")
        raise

    # Obtain speech timestamps (in frames)
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=SAMPLING_RATE, min_silence_duration_ms=500)
    
    if not speech_timestamps:
        logger.warning(f"No speech detected in {wav_path}")
        return []
        
    chunks = []
    current_chunk = []
    current_length = 0
    
    for ts in speech_timestamps:
        start_frame = ts['start']
        end_frame = ts['end']
        duration = end_frame - start_frame
        
        if current_length > 0 and (current_length + duration) / SAMPLING_RATE > target_max_sec:
            if current_length / SAMPLING_RATE >= target_min_sec:
                chunks.append(current_chunk)
                current_chunk = []
                current_length = 0
                
        current_chunk.append((start_frame, end_frame))
        current_length += duration
        
        if current_length / SAMPLING_RATE >= target_min_sec:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
            
    if current_length / SAMPLING_RATE >= target_min_sec:
        chunks.append(current_chunk)
    elif current_length > 0 and not chunks:
        # If the total speech is less than target_min_sec but it's the only one we have, save it anyway.
        chunks.append(current_chunk)
        
    out_files = []
    for i, c in enumerate(chunks):
        # Insert a short pause (200ms) between stitched segments if there are multiple segments in one chunk
        chunk_tensors = []
        pause_tensor = torch.zeros((1, int(0.2 * SAMPLING_RATE)))
        for j, (start, end) in enumerate(c):
            if j > 0:
                chunk_tensors.append(pause_tensor)
            # handle 1D or 2D tensor properly (silero read_audio returns 2D tensor usually: [1, seq_len])
            chunk_tensors.append(wav[0:1, start:end] if wav.dim() == 2 else wav[start:end].unsqueeze(0))
            
        if not chunk_tensors:
            continue
            
        final_tensor = torch.cat(chunk_tensors, dim=1)
        
        out_path = f"{output_prefix}_chunk{i:03d}.wav"
        save_audio(out_path, final_tensor, sampling_rate=SAMPLING_RATE)
        out_files.append(out_path)
        
    return out_files

def main():
    parser = argparse.ArgumentParser(description="Purify downloaded audio using Demucs and Silero VAD")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON file from scraper")
    parser.add_argument("--input-dir", required=True, help="Directory containing raw audio files")
    parser.add_argument("--output-dir", required=True, help="Directory for final chunked audio")
    parser.add_argument("--demucs-dir", default="data/temp_demucs", help="Temporary directory for Demucs output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.manifest):
        logger.error(f"Manifest not found: {args.manifest}")
        sys.exit(1)

    try:
        with open(args.manifest, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read manifest {args.manifest}: {e}")
        sys.exit(1)
        
    if isinstance(manifest, dict):
        manifest_items = list(manifest.values())
    elif isinstance(manifest, list):
        manifest_items = manifest
    else:
        logger.error("Manifest should be a JSON dict or list.")
        sys.exit(1)

    for idx, item in enumerate(manifest_items):
        try:
            # Validate required fields according to backend spec
            channel_id = item.get("channel_id")
            if not channel_id:
                raise ValueError(f"Missing required manifest column 'channel_id' at index {idx}")
                
            video_id = item.get("video_id")
            if not video_id:
                raise ValueError(f"Missing required manifest column 'video_id' at index {idx}")
                
            filename = item.get("filename")
            if not filename:
                raise ValueError(f"Missing required manifest column 'filename' at index {idx}")
                
            domain = item.get("domain", "Unknown")
            
            input_path = os.path.join(args.input_dir, filename)
            if not os.path.exists(input_path):
                logger.warning(f"Audio file not found for item {idx}: {input_path}")
                continue
                
            logger.info(f"Processing {video_id} ({domain}) for channel {channel_id}")
            
            # Step 1: Source Separation
            vocab_path = isolate_vocals(input_path, args.demucs_dir)
            
            # Step 2: VAD Slicing
            out_prefix_dir = os.path.join(args.output_dir, channel_id, domain)
            os.makedirs(out_prefix_dir, exist_ok=True)
            out_prefix = os.path.join(out_prefix_dir, video_id)
            
            chunks = chunk_with_silero(vocab_path, out_prefix)
            logger.info(f"Successfully generated {len(chunks)} chunks for {video_id}")
            
        except Exception as e:
            logger.error(f"Error processing item at index {idx}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
