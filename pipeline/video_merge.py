import subprocess
import os

def replace_audio_with_tts(original_video, tts_audio, output_path):
    """
    Replaces the original audio of the video with the TTS audio.
    
    Parameters:
    - original_video: path to the original MP4
    - tts_audio: path to the final aligned TTS MP3
    - output_path: path to save the dubbed video
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", original_video,
        "-i", tts_audio,
        "-c:v", "copy",          # keep video stream as-is
        "-map", "0:v:0",         # video from original
        "-map", "1:a:0",         # audio from TTS
        "-shortest",             # stop when shortest stream ends
        output_path
    ]

    subprocess.run(cmd, check=True)
    print(f"🎬 Dubbed video saved at: {output_path}")
