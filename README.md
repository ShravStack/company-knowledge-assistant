# Company Knowledge Assistant

A local Retrieval-Augmented Generation (RAG) assistant for company documents. Upload .pdf, .docx, or .txt files and ask grounded questions, get explanations, generate review questions, and get your answers auto-graded — all backed by your own documents.

## Features

- **Upload & Ingest** - parses, chunks, and embeds documents into a local vector store
- **Ask** - grounded Q&A over your documents via semantic search
- **Explain** - plain-language explanation of an uploaded document
- **Review** - auto-generates review/practice questions
- **Evaluate** - grades your answers with structured feedback
- **Document filtering** - scope any operation to one, several, or all documents

## Tech Stack

Python · FastAPI · Streamlit · ChromaDB · Sentence-Transformers · Google Gemini API · Pydantic

**Skills demonstrated:** RAG pipeline design, vector search, LLM API integration, prompt engineering, REST API design, full-stack Python development.

```

Runs entirely on the Gemini API + local embeddings by default — no other services required.

## Getting Started

**Prerequisites:** Python 3.10+, a [Gemini API key](https://aistudio.google.com/apikey) (free tier available)

```powershell
git clone https://github.com/ShravStack/company-knowledge-assistant.git
cd company-knowledge-assistant

cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
echo GEMINI_API_KEY=your_key_here > .env
```

### Run

**Terminal 1 - Backend** (must run from inside `backend/`)
```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn main:app --reload
```
→ `http://127.0.0.1:8000` (Swagger docs at `/docs`)

**Terminal 2 - Frontend**
```powershell
cd frontend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```
→ `http://localhost:8501`

## Known Limitations

- Chunking is character-based, not sentence-aware
- Scanned/image-only PDFs yield no text (no OCR)
- No authentication — local/personal use only
- Explain and Review operate on a slice of chunks, not the full document

## License

For educational/personal portfolio use.
