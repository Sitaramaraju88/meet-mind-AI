import sys
import os
import json
import time
from gtts import gTTS
from pydub import AudioSegment
import whisper

# ---------- LangChain / Chroma RAG imports ----------
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# ---------- INIT ----------
print("[INFO] Initializing SafeTalk AI...")

# ---------- STEP 0: Get audio file ----------
if len(sys.argv) < 2:
    print("[ERROR] No audio file provided!")
    sys.exit(1)

audio_file = sys.argv[1]
if not os.path.exists(audio_file):
    print(f"[ERROR] Audio file not found: {audio_file}")
    sys.exit(1)
print(f"[INFO] Audio file: {audio_file}")

# Convert MP3 to WAV if needed
if audio_file.endswith(".mp3"):
    print("[INFO] Converting MP3 to WAV...")
    sound = AudioSegment.from_mp3(audio_file)
    wav_file = "uploads/temp.wav"
    sound.export(wav_file, format="wav")
    audio_file = wav_file

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
unsafe_words = ["kill", "hate", "bomb"]
if any(word in text.lower() for word in unsafe_words):
    reply = "Sorry, I can't help with that request."
    print("[INFO] Unsafe content detected. Skipping RAG.")
else:
    # ---------- STEP 3: Greeting + RAG ----------
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    contains_greeting = any(word in text.lower() for word in greetings)
    is_question = "?" in text or any(q in text.lower() for q in ["what", "who", "how", "tell", "explain"])

    # ---------- RAG Setup ----------
    print("[INFO] Loading Hugging Face embeddings and Chroma DB...")
    start_time = time.time()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory="db", embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0),
        retriever=retriever
    )
    print(f"[INFO] Embeddings and Chroma DB loaded in {time.time() - start_time:.2f} sec")

    try:
        answer = qa_chain.run(text)
    except Exception as e:
        print(f"[ERROR] RAG failed: {e}")
        sys.exit(1)

    if contains_greeting:
        reply = f"Hello! {answer}"
    else:
        reply = answer

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
