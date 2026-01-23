import noisereduce as nr
import librosa
import soundfile as sf

# Load audio file
audio, sr = librosa.load(r"C:\Users\varma\OneDrive\Desktop\hack2\safe-talk-AI\uploads\response.mp3", sr=None)


# Reduce noise
reduced_noise = nr.reduce_noise(y=audio, sr=sr)

# Save the output
sf.write("output_audio.wav", reduced_noise, sr)

print("Noise reduced successfully!")
