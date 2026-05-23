import torch
import torchaudio

try:
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=False)
    get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks = utils
    
    # create a dummy wav file
    dummy = torch.zeros(1, 16000)
    torchaudio.save("dummy.wav", dummy, 16000)
    
    wav = read_audio("dummy.wav", sampling_rate=16000)
    print(f"wav dim: {wav.dim()}")
except Exception as e:
    print(f"Error: {e}")
