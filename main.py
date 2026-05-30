from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uuid
# =========================
# GEMINI SETUP
# =========================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# PDF READER
# =========================

def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text


# =========================
# TEXT CHUNKER
# =========================

def chunk_text(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_text(text)

    return chunks


# =========================
# EMBEDDING MODEL
# =========================

embedding_model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)

def create_embeddings(chunks):

    embeddings = embedding_model.encode(chunks)

    return embeddings


# =========================
# CHROMADB SETUP
# =========================

client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = client.get_or_create_collection(
    name="rag_collection"
)


def store_embeddings(chunks, embeddings, filename):

    for chunk, embedding in zip(chunks, embeddings):

        collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding.tolist()],
            documents=[chunk],
            metadatas=[
                {"source": filename}
            ]
        )

    return collection.count()

# =========================
# HOME ROUTE
# =========================

@app.get("/")
def home():

    return {

        "message": "RAG AI Assistant Running"
    }


# =========================
# PDF UPLOAD API
# =========================

@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # SAVE PDF

    file_location = f"../data/{file.filename}"

    with open(file_location, "wb") as f:

        f.write(await file.read())

    # READ PDF

    text = read_pdf(file_location)

    # CHUNK TEXT

    chunks = chunk_text(text)

    # CREATE EMBEDDINGS

    embeddings = create_embeddings(chunks)

    # STORE IN VECTOR DATABASE

    total_vectors = store_embeddings(
      chunks,
      embeddings,
      file.filename
)

    return {

        "filename": file.filename,

        "total_chunks": len(chunks),

        "embedding_dimension": len(embeddings[0]),

        "vectors_stored": total_vectors,

        "sample_chunk": chunks[0]
    }


# =========================
# QUERY MODEL
# =========================

query_model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)


# =========================
# ASK API
# =========================

@app.get("/ask/")
def ask_question(query: str):

    try:

        query_embedding = query_model.encode(query)

        results = collection.query(
            query_texts=[query],
               n_results=20
)

        retrieved_docs = results["documents"][0]
        sources = results["metadatas"][0]
        #SAFETY CHECK
        if not retrieved_docs:
            return {
                "question":query,
                "answer": " No relevant information found in database."
            }

        context = "\n\n".join(retrieved_docs)
        print("\n========== CONTEXT ==========\n")
        print(context) 
        print("\n=============================\n")

        prompt = f"""
You are a professional RAG assistant.

Answer ONLY from the provided context.

Context:
{context}

Question:
{query}


Rules:
- Do not hallucinate.
- Do not make up information.
- If information is not present, reply:
  Information not found in uploaded PDF.
- Keep answers concise and professional.

Answer:
"""

        response = gemini_model.generate_content(
            prompt
        )

        return {
           "question": query,
           "answer": response.text,
           "sources": sources
}

    except Exception as e:

        return {
            "error": str(e)
        }