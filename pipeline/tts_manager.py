import os
from pydub import AudioSegment

class TTSManager:
    """
    Manages post-TTS operations:
    - Timing alignment of TTS segments
    - Padding segments to match original video duration
    - Combining segments into one final track
    """

    def __init__(self, tts_dir="temp/tts_segments"):
        self.tts_dir = tts_dir
        self.aligned_dir = os.path.join(tts_dir, "aligned")
        os.makedirs(self.aligned_dir, exist_ok=True)

    def align_segments(self, segments):
        """
        Align individual TTS segments to match start/end times.
        Adds silence if necessary.
        """
        print("⏱ Aligning segments with padding...")
        for i, seg in enumerate(segments, start=1):
            src = os.path.join(self.tts_dir, f"segment_{i}.mp3")
            out = os.path.join(self.aligned_dir, f"segment_{i}.mp3")

            if not os.path.exists(src):
                print(f"⚠️ Segment {i} missing, skipping")
                continue

            start = seg.get("start", 0)
            end = seg.get("end", start + 0.5)
            target_duration = max(end - start, 0.3)

            audio = AudioSegment.from_mp3(src)
            current_duration = audio.duration_seconds

            if current_duration > 0:
                speed_factor = current_duration / target_duration
                aligned = audio._spawn(
                    audio.raw_data,
                    overrides={"frame_rate": int(audio.frame_rate * speed_factor)}
                ).set_frame_rate(audio.frame_rate)
            else:
                aligned = AudioSegment.silent(duration=int(target_duration * 1000))

            # Add silence at start if the segment doesn't start at 0
            if start > 0:
                aligned = AudioSegment.silent(duration=int(start * 1000)) + aligned

            aligned.export(out, format="mp3")

        print("✅ Segments aligned")

    def combine_segments(self, segments, output_path, total_duration=None):
        """
        Combine all aligned segments into one final audio track.
        Adds silence between segments and optionally pads to total_duration.
        """
        print("🔗 Combining aligned segments...")
        final_audio = AudioSegment.silent(duration=0)

        for i, seg in enumerate(segments, start=1):
            aligned_path = os.path.join(self.aligned_dir, f"segment_{i}.mp3")
            if not os.path.exists(aligned_path):
                continue

            audio = AudioSegment.from_mp3(aligned_path)
            last_end_ms = int(seg.get("end", 0) * 1000)

            # Add silence if needed
            if len(final_audio) < last_end_ms - len(audio):
                gap = (last_end_ms - len(audio)) - len(final_audio)
                final_audio += AudioSegment.silent(duration=gap)

            final_audio += audio

        # Pad at end if total_duration is specified
        if total_duration:
            total_ms = int(total_duration * 1000)
            if len(final_audio) < total_ms:
                final_audio += AudioSegment.silent(duration=(total_ms - len(final_audio)))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_audio.export(output_path, format="mp3")
        print(f"✅ Combined final audio saved at: {output_path}")
        return output_path
