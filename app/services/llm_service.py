import requests
from http import HTTPStatus
from app.config import OLLAMA_API_URL
from app.logger.logger import log


def enrich_task_with_llm(title: str) -> str:
    prompt = (
        f"You are a project assistant. Based on the following task title, "
        f"write a clear, concise task description in 2-3 sentences.\n"
        f"Task title: {title}"
    )

    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=data)
        log.debug(f"LLM response: {response.status_code} - {response.text}")

        response.raise_for_status()

        enriched_description = response.json().get("response", "")
        if not enriched_description:
            log.warning("LLM returned an empty response")
        return enriched_description

    except requests.RequestException as e:
        log.error(f"Error communicating with Ollama LLM: {e}", HTTPStatus.INTERNAL_SERVER_ERROR)
        raise RuntimeError("Failed to enrich task using LLM")
