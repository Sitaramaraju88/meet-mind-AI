import assemblyai as aai
import os

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def run_speaker_diarization(wav_path):
    print("🎙 Running speaker diarization (AssemblyAI)...")

    config = aai.TranscriptionConfig(
        speaker_labels=True
    )

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(wav_path, config)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(transcript.error)

    speakers = []

    for utterance in transcript.utterances:
        speakers.append({
            "speaker": utterance.speaker,
            "start": utterance.start / 1000.0,  # ms → seconds
            "end": utterance.end / 1000.0
        })
        print(f"🗣 Speaker {utterance.speaker}: {utterance.start/1000:.2f}s → {utterance.end/1000:.2f}s")

    return speakers
