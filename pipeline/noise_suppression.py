import librosa
import noisereduce as nr
import soundfile as sf
import os

def denoise_audio(input_wav, output_wav):
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)

    print("🧹 Loading audio for noise suppression...")
    y, sr = librosa.load(input_wav, sr=None)

    print("🔇 Reducing noise...")
    reduced = nr.reduce_noise(y=y, sr=sr)

    sf.write(output_wav, reduced, sr)

    print("✅ Noise suppressed audio saved:", output_wav)
