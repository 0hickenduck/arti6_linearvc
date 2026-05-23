import os
import whisper
from pydub import AudioSegment
import warnings
import json

def generate_demo():
    print("Loading Whisper large-v2...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = whisper.load_model("large-v2")
    
    # Pick another FuwaMoco file (Hopefully pure talking/zatsudan)
    test_file = "data/vtuber_clean/clean_-UBdZ4tykfI.wav"
    out_dir = "data/demo_segments_zatsudan"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Transcribing {test_file} for demo...")
    
    # Transcribe
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = model.transcribe(
            test_file,
            task="transcribe",
            condition_on_previous_text=False,
            initial_prompt="こんにちは、元気ですか。Hello, how are you?"
        )
        
    audio = AudioSegment.from_wav(test_file)
    
    valid_count = 0
    current_audio = AudioSegment.empty()
    current_text = []
    current_duration_ms = 0
    
    print("Slicing audio...")
    for segment in result["segments"]:
        if valid_count >= 50:
            break
            
        text = segment["text"].strip()
        # Strict threshold to 0.4 to prevent blank noise
        if segment.get("no_speech_prob", 0) > 0.4:
            continue
            
        if not text or "[" in text or "]" in text or "(" in text or ")" in text or "♪" in text or "*" in text:
            continue
            
        start_ms = max(0, int(segment["start"] * 1000) - 200)
        end_ms = min(len(audio), int(segment["end"] * 1000) + 200)
        dur = end_ms - start_ms
        
        if dur < 500:
            continue
            
        chunk = audio[start_ms:end_ms]
        
        if current_duration_ms > 0:
            current_audio += AudioSegment.silent(duration=200)
            current_duration_ms += 200
            
        current_audio += chunk
        current_text.append(text)
        current_duration_ms += dur
        
        if current_duration_ms >= 4000:
            out_wav = os.path.join(out_dir, f"demo_v2_{valid_count:02d}.wav")
            out_txt = os.path.join(out_dir, f"demo_v2_{valid_count:02d}.txt")
            current_audio.export(out_wav, format="wav")
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(" ".join(current_text))
            
            valid_count += 1
            current_audio = AudioSegment.empty()
            current_text = []
            current_duration_ms = 0
            
    print(f"Generated {valid_count} demo chunks in {out_dir}")

if __name__ == "__main__":
    generate_demo()
