import os

from dotenv import load_dotenv
from google import genai

from config import GEMINI_MODEL


load_dotenv()


def ask_gemini_chat(system_prompt: str, user_prompt: str) -> str:
    """
    Uses Gemini API for final answer generation.
    Faster than local Ollama because it runs on Google servers.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Create backend/.env and add GEMINI_API_KEY=your_key_here"
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
SYSTEM INSTRUCTIONS:
{system_prompt}

USER REQUEST:
{user_prompt}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response.text:
        return "No response returned from Gemini."

    return response.text