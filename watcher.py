import os
import time
from pathlib import Path
from main import synthesize_tts, main as main_pipeline  # your existing pipeline
from tts_manager import TTSManager

WATCH_FOLDER = Path("input_media")
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)

processed_files = set()

def process_new_video(video_path: Path):
    print(f"\n🎬 Processing {video_path.name} ...")

    # Run your existing pipeline (extraction, STT, translation, TTS)
    main_pipeline(video_path)

    # Initialize TTS manager
    tts_manager = TTSManager()
    segments_folder = Path("temp/tts_segments")  # where TTS MP3s are saved

    # Combined TTS audio
    combined_audio_path = OUTPUT_FOLDER / f"{video_path.stem}_dubbed_audio.mp3"
    tts_manager.combine_tts_segments(segments_folder, combined_audio_path)

    # Final dubbed video
    final_video_path = OUTPUT_FOLDER / f"dubbed_{video_path.name}"
    tts_manager.merge_audio_with_video(str(video_path), str(combined_audio_path), str(final_video_path))

    print(f"✅ Finished processing: {video_path.name}")
    print(f"🎞 Dubbed video saved to: {final_video_path}")


def watch_folder():
    print(f"👀 Watching folder: {WATCH_FOLDER.resolve()} ...")
    while True:
        for video_file in WATCH_FOLDER.glob("*.mp4"):
            if video_file not in processed_files:
                try:
                    process_new_video(video_file)
                    processed_files.add(video_file)
                except Exception as e:
                    print(f"⚠️ Error processing {video_file.name}: {e}")
        time.sleep(5)


if __name__ == "__main__":
    watch_folder()
