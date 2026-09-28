import os

# Project root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Uploaded files will be stored here
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")

# ChromaDB vector database will be stored here
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Chroma collection name
COLLECTION_NAME = "company_documents"

# Ollama local server
OLLAMA_BASE_URL = "http://localhost:11434"

# Ollama model used for local fallback answer generation
OLLAMA_CHAT_MODEL = "llama3.2:1b"

# Embedding provider
# Options: "sentence_transformers" or "ollama"
EMBEDDING_PROVIDER = "sentence_transformers"

# Sentence Transformers model for local batch embeddings
SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Batch size for faster document embedding
# If your laptop becomes slow, change 32 to 16
EMBEDDING_BATCH_SIZE = 16

# Ollama embedding model used for RAG search
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

# LLM provider for final answer generation
# Options: "ollama" or "gemini"
LLM_PROVIDER = "gemini"

# Gemini model used for fast cloud answer generation
GEMINI_MODEL = "gemini-flash-lite-latest"

# Better for long documents
CHUNK_SIZE = 2500
CHUNK_OVERLAP = 100

# Retrieval settings
DEFAULT_TOP_K = 3

# Long document summarization settings
SUMMARY_BATCH_SIZE = 10
MAX_SUMMARY_CHUNKS = 25
MAX_QUESTION_CONTEXT_CHUNKS = 15

# Fast review question generation setting
MAX_REVIEW_CONTEXT_CHUNKS = 8


# Fast explanation generation setting
MAX_EXPLANATION_CONTEXT_CHUNKS = 10