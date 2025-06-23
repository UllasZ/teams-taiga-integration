from http import HTTPStatus

import requests

from app.config import OLLAMA_API_URL
from app.logger.logger import log


def call_llm(prompt: str, model: str = "llama3", timeout: int = 15) -> str:
    """Internal helper to send a prompt to the LLM and return the response text."""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        log.debug(f"LLM response: {response.status_code}")
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as e:
        log.error(f"Error communicating with Ollama LLM: {e}", HTTPStatus.INTERNAL_SERVER_ERROR)
        raise RuntimeError("Failed to communicate with LLM")
