import subprocess
import os
import shutil
import sys

def isolate(audio_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cmd = [sys.executable, '-m', 'demucs.separate', '-n', 'htdemucs', '--out', output_dir, audio_path]
    subprocess.run(cmd, check=True)
    
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    vocals_path = os.path.join(output_dir, 'htdemucs', base_name, 'vocals.wav')
    
    final_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
    if os.path.exists(vocals_path):
        shutil.copy(vocals_path, final_path)
    else:
        raise FileNotFoundError(f"Vocals not found at {vocals_path}")
        
    return final_path
