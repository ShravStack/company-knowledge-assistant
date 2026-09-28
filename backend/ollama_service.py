from typing import List

import requests

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
    OLLAMA_EMBEDDING_MODEL,
)


def check_ollama_running() -> dict:
    """
    Checks whether Ollama is running and returns available models.
    """
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10
        )
        response.raise_for_status()

        return {
            "status": "running",
            "models": response.json().get("models", [])
        }

    except Exception as e:
        return {
            "status": "not_running",
            "error": str(e)
        }


def get_ollama_embedding(text: str) -> List[float]:
    """
    Converts text into embedding using Ollama embedding model.

    Used only if EMBEDDING_PROVIDER = "ollama".
    """
    payload = {
        "model": OLLAMA_EMBEDDING_MODEL,
        "input": text
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    data = response.json()

    embeddings = data.get("embeddings", [])

    if not embeddings:
        raise ValueError("Ollama did not return embeddings.")

    return embeddings[0]


def ask_ollama_chat(system_prompt: str, user_prompt: str) -> str:
    """
    Uses local Ollama chat model for final answer generation.
    """
    payload = {
        "model": OLLAMA_CHAT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=300
    )

    response.raise_for_status()
    data = response.json()

    return data["message"]["content"]