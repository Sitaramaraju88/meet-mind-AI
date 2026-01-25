from pipeline.audio_extraction import extract_audio
from pipeline.noise_suppression import denoise_audio
from pipeline.vad import detect_speech
from pipeline.diarization import diarize_audio
from pipeline.stt import transcribe
from pipeline.tts import synthesize

def dub_video(input_video, output_audio):
    raw_audio = "temp.wav"
    clean_audio = "clean.wav"

    # 1. Extract audio
    extract_audio(input_video, raw_audio)

    # 2. Noise suppression
    denoise_audio(raw_audio, clean_audio)

    # 3. VAD
    segments = detect_speech(clean_audio)

    # 4. Speaker Diarization
    diarization = diarize_audio(clean_audio)

    # 5. STT
    transcription = transcribe(clean_audio)

    # 6. TTS
    synthesize(transcription["text"], output_audio)

    print(f"Dubbed audio ready: {output_audio}")
