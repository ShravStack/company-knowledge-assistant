# Company RAG Chatbot

This is a free local RAG-based chatbot for company documents.

## Features

- Upload company documents
- Supports .txt, .pdf, .docx
- Stores document embeddings in local ChromaDB
- Uses Ollama local LLM
- Answers questions from uploaded documents
- Explains uploaded documents
- Generates review question sets

## Models Used

- llama3.2:1b for answering questions
- nomic-embed-text for embeddings

## Backend

FastAPI backend runs on:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

## Frontend

Streamlit frontend runs on:

http://localhost:8501