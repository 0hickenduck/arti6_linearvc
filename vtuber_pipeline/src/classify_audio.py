import whisper
import os
import warnings

def classify(audio_path):
    # Suppress warnings from FP16 on CPU if applicable
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = whisper.load_model("base")
        
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
        
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        
        return {
            'language': detected_lang,
            'is_singing': True
        }
