# Company Knowledge Assistant

A local RAG (Retrieval Augmented Generation) assistant for company documents. Upload pdf, docx, or txt files and the app can answer questions, explain documents, generate review questions, and grade your answers to those questions, all based on the documents you uploaded.

## Features

- Upload documents and store them as embeddings in a local vector database
- Ask questions and get answers grounded in your documents
- Get plain language explanations of a document
- Generate review questions from a document
- Get your answers to review questions graded automatically
- Filter any of the above to specific documents

## Tech Stack

Python, FastAPI, Streamlit, ChromaDB, Sentence Transformers, Google Gemini API, Pydantic

Skills used: RAG pipeline design, vector search, LLM API integration, prompt engineering, REST API design, full-stack Python development.

## Architecture

`frontend/app.py` talks to `backend/main.py` over HTTP. The backend uses a `RAGService` class that handles document loading and chunking, embeddings, ChromaDB storage and search, and calls the Gemini API for generation.

Runs entirely on the Gemini API and local embeddings by default, no other services needed.

## Getting Started

Needs Python 3.10 or higher and a Gemini API key from Google AI Studio (free tier available).

```
git clone https://github.com/ShravStack/company-knowledge-assistant.git
cd company-knowledge-assistant

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add your key to a `.env` file in `backend/` as `GEMINI_API_KEY=your_key_here`

## Running

Backend, must be run from inside the `backend` folder:

```
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

Runs at `http://127.0.0.1:8000`, docs at `/docs`

Frontend, in a separate terminal:

```
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Runs at `http://localhost:8501`

## Known Limitations

- Chunking is character based, not sentence aware
- Scanned or image only pdfs will not extract any text
- No authentication, meant for local or personal use only
- Explain and review only look at a slice of the document, not the full text

## License

For personal and educational use.
