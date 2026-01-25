import torch
import soundfile as sf
import numpy as np
from silero_vad import get_speech_timestamps, load_silero_vad

def run_vad(wav_path):
    print(f"🎙 Running VAD on: {wav_path}")

    # Load Silero VAD model
    model = load_silero_vad()

    # Load audio using soundfile
    waveform_np, sr = sf.read(wav_path)  # waveform_np is float32 numpy array

    # Convert to torch tensor
    if len(waveform_np.shape) > 1:
        # Multi-channel -> mono
        waveform_np = np.mean(waveform_np, axis=1)

    waveform = torch.from_numpy(waveform_np).float().unsqueeze(0)  # (1, n_samples)

    # Resample to 16 kHz if needed
    if sr != 16000:
        waveform = torch.from_numpy(
            np.interp(
                np.linspace(0, len(waveform_np), int(len(waveform_np) * 16000 / sr)),
                np.arange(len(waveform_np)),
                waveform_np
            )
        ).unsqueeze(0)
        sr = 16000

    # Get speech segments
    speech_timestamps = get_speech_timestamps(
        waveform,
        model,
        sampling_rate=sr
    )

    print("🧠 VAD segments:")
    for seg in speech_timestamps:
        print(seg)

    return speech_timestamps
