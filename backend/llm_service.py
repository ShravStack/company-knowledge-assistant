from config import LLM_PROVIDER
from gemini_service import ask_gemini_chat
from ollama_service import ask_ollama_chat


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Main LLM function used by RAG service.

    It chooses the final answer model based on config.py:

    LLM_PROVIDER = "gemini"  -> uses Gemini API
    LLM_PROVIDER = "ollama"  -> uses local Ollama
    """
    provider = LLM_PROVIDER.lower().strip()

    if provider == "gemini":
        return ask_gemini_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    if provider == "ollama":
        return ask_ollama_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    raise ValueError(
        "Invalid LLM_PROVIDER in config.py. Use 'gemini' or 'ollama'."
    )