from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_PROVIDER,
    SENTENCE_TRANSFORMER_MODEL,
    EMBEDDING_BATCH_SIZE,
)

from ollama_service import get_ollama_embedding


@lru_cache(maxsize=1)
def get_sentence_transformer_model() -> SentenceTransformer:
    """
    Loads SentenceTransformer model only once and reuses it.

    First run may take time because the model downloads from Hugging Face.
    Later runs are faster because it is cached locally.
    """
    return SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)


def get_text_embedding(text: str) -> List[float]:
    """
    Returns embedding for one text.
    Used for user question embedding during retrieval.
    """
    provider = EMBEDDING_PROVIDER.lower().strip()

    if provider == "sentence_transformers":
        model = get_sentence_transformer_model()

        embedding = model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    if provider == "ollama":
        return get_ollama_embedding(text)

    raise ValueError(
        "Invalid EMBEDDING_PROVIDER. Use 'sentence_transformers' or 'ollama'."
    )


def get_text_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Returns embeddings for many texts in batches.

    This is the main speed improvement for document processing.
    """
    provider = EMBEDDING_PROVIDER.lower().strip()

    if provider == "sentence_transformers":
        model = get_sentence_transformer_model()

        embeddings = model.encode(
            texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.tolist()

    if provider == "ollama":
        return [
            get_ollama_embedding(text)
            for text in texts
        ]

    raise ValueError(
        "Invalid EMBEDDING_PROVIDER. Use 'sentence_transformers' or 'ollama'."
    )