import ffmpeg
import os

def extract_audio(video_path, wav_out):
    os.makedirs(os.path.dirname(wav_out), exist_ok=True)

    (
        ffmpeg
        .input(video_path)
        .output(wav_out, ac=1, ar=16000)
        .overwrite_output()
        .run()
    )

    print("✅ Audio extracted:", wav_out)
