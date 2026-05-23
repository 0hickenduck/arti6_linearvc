import os
import glob
import whisper
from pydub import AudioSegment
import json
import traceback

def segment_dataset(input_dir, output_dir, model_size="large-v2", min_chunk_len_ms=4000):
    print(f"Loading Whisper model '{model_size}'...")
    # Add warnings catch to avoid fp16 warnings
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = whisper.load_model(model_size)
    
    os.makedirs(output_dir, exist_ok=True)
    
    wav_files = glob.glob(os.path.join(input_dir, "clean_*.wav"))
    print(f"Found {len(wav_files)} files to segment.")
    
    total_chunks = 0
    
    for i, file_path in enumerate(wav_files):
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"[{i+1}/{len(wav_files)}] Transcribing & Segmenting {base_name}...")
        
        try:
            # Transcribe with language detection enabled automatically
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = model.transcribe(file_path)
            
            audio = AudioSegment.from_wav(file_path)
            
            valid_count = 0
            
            # Stitching buffers
            current_audio = AudioSegment.empty()
            current_text = []
            current_duration_ms = 0
            
            for j, segment in enumerate(result["segments"]):
                text = segment["text"].strip()
                
                # Confidence Filtering
                no_speech_prob = segment.get("no_speech_prob", 0)
                if no_speech_prob > 0.4:
                    continue
                    
                # Semantic Filtering
                if not text:
                    continue
                if "[" in text and "]" in text:
                    continue
                if "(" in text and ")" in text:
                    continue
                if "♪" in text or "*" in text:
                    continue
                    
                # Timestamps in ms (with slight padding to avoid harsh cuts)
                start_ms = max(0, int(segment["start"] * 1000) - 200)
                end_ms = min(len(audio), int(segment["end"] * 1000) + 200)
                
                dur = end_ms - start_ms
                if dur < 500: # Ignore absurdly short blips entirely
                    continue
                    
                chunk = audio[start_ms:end_ms]
                
                # Accumulate
                if current_duration_ms > 0:
                    # Add 200ms of silence between stitched segments to sound natural
                    current_audio += AudioSegment.silent(duration=200)
                    current_duration_ms += 200
                
                current_audio += chunk
                current_text.append(text)
                current_duration_ms += dur
                
                # If we have reached the minimum chunk length (e.g., 4 seconds)
                if current_duration_ms >= min_chunk_len_ms:
                    # Save it
                    out_wav = os.path.join(output_dir, f"{base_name}_stitched_{valid_count:04d}.wav")
                    out_txt = os.path.join(output_dir, f"{base_name}_stitched_{valid_count:04d}.txt")
                    
                    current_audio.export(out_wav, format="wav")
                    with open(out_txt, "w", encoding="utf-8") as f:
                        f.write(" ".join(current_text))
                        
                    valid_count += 1
                    total_chunks += 1
                    
                    # Reset buffers
                    current_audio = AudioSegment.empty()
                    current_text = []
                    current_duration_ms = 0
            
            # Save any remaining buffer if it's long enough (e.g. > 2s)
            if current_duration_ms > 2000:
                out_wav = os.path.join(output_dir, f"{base_name}_stitched_{valid_count:04d}.wav")
                out_txt = os.path.join(output_dir, f"{base_name}_stitched_{valid_count:04d}.txt")
                current_audio.export(out_wav, format="wav")
                with open(out_txt, "w", encoding="utf-8") as f:
                    f.write(" ".join(current_text))
                valid_count += 1
                total_chunks += 1
                
            print(f"  -> Extracted {valid_count} stitched chunks (>= 4s).")
            
        except Exception as e:
            print(f"  -> Failed processing {base_name}: {e}")
            traceback.print_exc()

    print(f"\nSegmentation complete! Total stitched chunks extracted: {total_chunks}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/vtuber_clean", help="Input directory")
    parser.add_argument("--output", default="data/vtuber_segmented", help="Output directory")
    parser.add_argument("--model", default="large-v2", help="Whisper model size")
    args = parser.parse_args()
    
    segment_dataset(args.input, args.output, args.model)
