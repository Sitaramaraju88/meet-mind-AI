import os
import whisper
from gtts import gTTS
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from groq import Groq

print("[INIT] Starting app.py module load...")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

VECTOR_DB_FILE = os.path.join(os.path.dirname(__file__), "..", "db.txt")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Load models
print("[INIT] Loading Whisper model...")
_whisper_model = whisper.load_model("base")
print("[INIT] Loading SentenceTransformer model...")
_st_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load DB
print(f"[INIT] Loading vector DB from {VECTOR_DB_FILE}...")
try:
    with open(VECTOR_DB_FILE, "r", encoding="utf-8") as f:
        DOCUMENTS = [line.strip() for line in f if line.strip()]
    print(f"[INIT] Loaded {len(DOCUMENTS)} documents")
except FileNotFoundError:
    print(f"[WARN] db.txt not found, using empty documents")
    DOCUMENTS = ["No documents loaded. Please add content to db.txt"]

_doc_embeddings = _st_model.encode(DOCUMENTS)
_index = faiss.IndexFlatL2(_doc_embeddings.shape[1])
_index.add(np.array(_doc_embeddings))
print("[INIT] Vector index built")

# Utility functions
def transcribe_audio(file_path: str) -> str:
    return _whisper_model.transcribe(file_path)["text"]

def query_vector_db(text: str) -> str:
    """
    Retrieves relevant context from vector DB and uses Groq to generate
    a concise, natural response based on the context.
    """
    try:
        # Get top 3 most relevant documents
        query_emb = _st_model.encode([text])
        k = min(3, len(DOCUMENTS))
        D, I = _index.search(np.array(query_emb), k=k)
        
        # Gather context from top matches
        context_docs = [DOCUMENTS[I[0][i]] for i in range(k)]
        context = "\n".join(context_docs)
        
        print(f"[DEBUG] Retrieved context: {context[:200]}...")
        
        # Use Groq to generate a natural response
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. Based on the provided context, "
                        "answer the user's question concisely in 2-3 sentences. "
                        "If the context doesn't contain the answer, say so politely. "
                        "Keep responses under 200 characters for text-to-speech."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {text}\n\nAnswer:"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=100,
            top_p=1,
            stream=False
        )
        
        reply = chat_completion.choices[0].message.content.strip()
        print(f"[DEBUG] Groq response: {reply}")
        
        # Ensure response isn't too long for TTS
        if len(reply) > 250:
            reply = reply[:247] + "..."
        
        return reply
        
    except Exception as e:
        print(f"[ERROR] Groq API error: {str(e)}")
        # Fallback to simple retrieval if Groq fails
        query_emb = _st_model.encode([text])
        D, I = _index.search(np.array(query_emb), k=1)
        fallback_reply = DOCUMENTS[I[0][0]]
        
        # Truncate fallback
        if len(fallback_reply) > 200:
            fallback_reply = fallback_reply[:197] + "..."
        
        return fallback_reply

def text_to_speech(text: str, out_path: str):
    """
    Convert text to speech with error handling
    """
    try:
        # Ensure text isn't too long
        if len(text) > 250:
            text = text[:247] + "..."
        
        print(f"[DEBUG] TTS input: {text}")
        tts = gTTS(text, lang='en', slow=False)
        tts.save(out_path)
        
        # Verify file creation
        if os.path.exists(out_path):
            file_size = os.path.getsize(out_path)
            print(f"[DEBUG] TTS file created: {file_size} bytes")
        else:
            raise Exception("TTS file was not created")
            
    except Exception as e:
        print(f"[ERROR] TTS failed: {str(e)}")
        raise Exception(f"Text-to-speech failed: {str(e)}")

print("[INIT] app.py module loaded successfully")