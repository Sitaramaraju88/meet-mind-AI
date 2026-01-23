import sys
import os
import time
import json
import whisper
from groq import Groq
from gtts import gTTS

# ---------- INIT ----------
print("[INFO] Initializing SafeTalk AI...")

# Groq client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("[ERROR] GROQ_API_KEY not set!")
    sys.exit(1)
client = Groq(api_key=api_key)
print("[INFO] Groq client initialized.")

# ---------- GET AUDIO FILE ----------
if len(sys.argv) < 2:
    print("[ERROR] No audio file provided!")
    sys.exit(1)

audio_file = sys.argv[1]
if not os.path.exists(audio_file):
    print(f"[ERROR] Audio file not found: {audio_file}")
    sys.exit(1)
print(f"[INFO] Audio file: {audio_file}")

# ---------- STEP 1: Speech to Text ----------
print("[INFO] Loading Whisper model (tiny for speed, CPU)...")
start_time = time.time()
model = whisper.load_model("tiny")
print(f"[INFO] Whisper model loaded in {time.time() - start_time:.2f} sec")

print("[INFO] Transcribing audio...")
start_time = time.time()
try:
    result = model.transcribe(audio_file)
    text = result["text"]
except Exception as e:
    print(f"[ERROR] Whisper transcription failed: {e}")
    sys.exit(1)
print(f"[INFO] Transcription done in {time.time() - start_time:.2f} sec. Text: {text}")

# ---------- STEP 2: Safety Check ----------
# unsafe_words = ["kill", "hate", "bomb"]
# if any(word in text.lower() for word in unsafe_words):
#     reply = "Sorry, I can't help with that request."
#     print("[INFO] Unsafe content detected. Skipping LLM.")
# else:
    # ---------- STEP 3: LLM Response (Groq) ----------
print("[INFO] Sending text to Groq LLM...")
start_time = time.time()
try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are SafeTalk AI. Be safe, professional, and enterprise-ready."},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    reply = completion.choices[0].message.content
except Exception as e:
    print(f"[ERROR] Groq LLM failed: {e}")
    sys.exit(1)
print(f"[INFO] Groq response received in {time.time() - start_time:.2f} sec. Reply: {reply}")

# ---------- STEP 4: Text to Speech ----------
print("[INFO] Converting text to speech...")
start_time = time.time()
try:
    tts = gTTS(reply)
    audio_out = "uploads/response.mp3"
    tts.save(audio_out)
except Exception as e:
    print(f"[ERROR] gTTS failed: {e}")
    sys.exit(1)
print(f"[INFO] Audio saved in {time.time() - start_time:.2f} sec -> {audio_out}")

# ---------- STEP 5: Output JSON ----------
output = {
    "text": text,
    "audio": audio_out
}
print("[INFO] Process complete. Sending JSON output...")
print(json.dumps(output))
