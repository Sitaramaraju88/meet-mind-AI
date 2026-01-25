# pipeline/stt.py
import assemblyai as aai
import os

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def run_stt(wav_path, speaker_segments=None):
    print(f"🎙 Running STT on: {wav_path}")

    # Configure transcription
    config = aai.TranscriptionConfig(
        speaker_labels=True  # enables speaker info in AssemblyAI
    )

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(wav_path, config)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(transcript.error)

    print("\n📝 Full transcript:")
    print(transcript.text, "\n")

    # Print per-speaker segments
    print("🗣 Transcripts by speaker:")
    if transcript.utterances:
        for utterance in transcript.utterances:
            start_s = utterance.start / 1000
            end_s = utterance.end / 1000
            speaker = utterance.speaker
            text = utterance.text
            print(f"{speaker}: {start_s:.2f}s → {end_s:.2f}s | {text}")
    else:
        print("No speaker segments found!")

    # Return utterances if needed
    return transcript.utterances
