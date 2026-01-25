def synthesize_tts(segments, voice_id):
    import os
    from elevenlabs.client import ElevenLabs

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
