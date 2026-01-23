import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_TEXT_PATH = os.path.join(BASE_DIR, "db.txt")
PERSIST_DIR = os.path.join(BASE_DIR, "vector_db")

with open(DB_TEXT_PATH, "r", encoding="utf-8") as f:
    raw_text = f.read()

print("db.txt loaded")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_text(raw_text)
documents = [Document(page_content=c) for c in chunks]

print(f"Split into {len(documents)} chunks")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory=PERSIST_DIR
)

db.persist()

print("Vector DB created successfully")
