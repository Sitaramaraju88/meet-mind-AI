import os
from pathlib import Path
from deep_translator import GoogleTranslator
from elevenlabs.client import ElevenLabs
import subprocess

from pipeline.audio_extraction import extract_audio
from pipeline.noise_suppression import denoise_audio
from pipeline.diarization import run_speaker_diarization
from pipeline.stt import run_stt
from pipeline.text_segmentation import segment_text
from pipeline.tts_manager import TTSManager

# ------------------- HELPERS -------------------

def get_video_duration(video_path):
    """Return video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def replace_audio_in_video(original_video, tts_audio, output_path):
    """Replace original video audio with TTS audio using ffmpeg."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(original_video),
        "-i", str(tts_audio),
        "-c:v", "copy",          # keep original video stream
        "-map", "0:v:0",         # video stream
        "-map", "1:a:0",         # TTS audio stream
        "-shortest",
        str(output_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"🎬 Dubbed video saved at: {output_path}")

# ------------------- TTS -------------------

def synthesize_tts(segments, voice_id):
    os.makedirs("temp/tts_segments", exist_ok=True)
    print("🎙 Synthesizing speech with ElevenLabs API...")

    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    for i, seg in enumerate(segments, start=1):
        text = seg.get("translated_text", "").strip()
        if not text:
            continue

        print(f"  💬 Generating TTS for segment {i}...")
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        mp3_path = f"temp/tts_segments/segment_{i}.mp3"
        with open(mp3_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        print(f"  🎧 Saved: {mp3_path}")

    print("✅ TTS generation completed!")

# ------------------- MAIN PIPELINE -------------------

def main(video_path="input_media/sample.mp4"):
    step1_wav = "temp/step1_extracted.wav"
    step2_wav = "temp/step2_denoised.wav"
    os.makedirs("temp", exist_ok=True)

    # 1️⃣ Audio extraction & preprocessing
    print("🎬 Extracting audio...")
    extract_audio(video_path, step1_wav)

    print("🧹 Denoising audio...")
    denoise_audio(step1_wav, step2_wav)

    print("🎙 Running diarization...")
    speakers = run_speaker_diarization(step2_wav)

    print("📝 Running STT...")
    stt_results = run_stt(step2_wav, speaker_segments=speakers)

    print("✂️ Segmenting text...")
    segments = segment_text(stt_results)

    # 2️⃣ Translation
    print("🌐 Translating to hi...")
    translator = GoogleTranslator(source="auto", target="hi")
    for seg in segments:
        text = seg.get("text", "")
        seg["translated_text"] = translator.translate(text) if text else ""
    print("✅ Translation completed!")

    # 3️⃣ Voice selection & TTS
    print("🎤 Fetching available voices...")
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    voices_response = client.voices.get_all()
    voices = voices_response.voices

    selected_voice = voices[0]
    voice_id = selected_voice.voice_id
    voice_name = selected_voice.name
    print(f"✅ Using voice: {voice_name} ({voice_id})")

    synthesize_tts(segments, voice_id)

    # 4️⃣ TTS Manager: Align & combine
    video_duration = get_video_duration(video_path)
    print(f"⏱ Original video duration: {video_duration:.2f}s")

    tts_manager = TTSManager()
    tts_manager.align_segments(segments)  # pads segments
    final_tts_path = tts_manager.combine_segments(
        segments,
        output_path="temp/tts_segments/final_aligned.mp3",
        total_duration=video_duration
    )
    print(f"🎵 Final aligned TTS saved at: {final_tts_path}")

    # 5️⃣ Merge final TTS with original video
    output_video_path = Path("output") / f"dubbed_{Path(video_path).name}"
    replace_audio_in_video(video_path, final_tts_path, output_video_path)

# ------------------- ENTRY POINT -------------------

if __name__ == "__main__":
    main()
