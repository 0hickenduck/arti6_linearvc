#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SEEDVC_ROOT = REPO_ROOT / "external" / "seed-vc"
DATA_DIR = REPO_ROOT / "data" / "vtuber_clean"
OUTPUT_DIR = REPO_ROOT / "outputs" / "vtuber_demo"

def main():
    if not SEEDVC_ROOT.exists():
        print("Error: seed-vc not found in external/seed-vc")
        sys.exit(1)
        
    source_wav = DATA_DIR / "vocals.wav"
    target_wav = DATA_DIR / "Example_vocals.wav"
    
    if not source_wav.exists() or not target_wav.exists():
        print("Error: Source or target wav not found in data/vtuber_clean")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    command = [
        sys.executable,
        "inference.py",
        "--source", str(source_wav),
        "--target", str(target_wav),
        "--output", str(OUTPUT_DIR),
        "--diffusion-steps", "15",
        "--f0-condition", "True",
        "--auto-f0-adjust", "False"
    ]
    
    print("Running Seed-VC inference on VTuber data...")
    print(f"Source: {source_wav.name}")
    print(f"Target: {target_wav.name}")
    
    env = dict(PYTHONPATH=".")
    
    completed = subprocess.run(
        command,
        cwd=SEEDVC_ROOT,
        env=env,
        text=True,
    )
    
    if completed.returncode == 0:
        print(f"\nSuccess! Output saved to {OUTPUT_DIR}")
    else:
        print("\nError running inference.")
        sys.exit(1)

if __name__ == "__main__":
    main()
