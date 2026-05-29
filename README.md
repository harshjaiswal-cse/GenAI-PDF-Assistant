# GenAI PDF Assistant

A Retrieval-Augmented Generation (RAG) based PDF Question Answering Assistant built using FastAPI, ChromaDB, SentenceTransformers, and Google Gemini.

## Features

* Upload PDF documents
* Extract text from PDFs
* Generate embeddings using SentenceTransformers
* Store vectors in ChromaDB
* Semantic search over documents
* AI-powered answers using Google Gemini
* Source-aware retrieval
* Persistent vector database storage

## Tech Stack

* FastAPI
* Python
* ChromaDB
* SentenceTransformers
* Google Gemini
* PyPDF
* LangChain Text Splitters

## Workflow

1. Upload PDF
2. Extract text
3. Split into chunks
4. Generate embeddings
5. Store vectors in ChromaDB
6. Retrieve relevant chunks
7. Generate answer using Gemini

## Run Locally

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
