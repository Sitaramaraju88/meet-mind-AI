# pipeline/text_segmentation.py
def segment_text(stt_results):
    print("✂️ Segmenting text...")
    segments = []

    for seg in stt_results:
        # Access attributes directly instead of using .get()
        speaker = seg.speaker
        start = seg.start / 1000.0  # convert ms to seconds
        end = seg.end / 1000.0
        text = seg.text

        segments.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "text": text
        })

    print(f"✅ Created {len(segments)} text segments")
    return segments
