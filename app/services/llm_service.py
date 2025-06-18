import difflib
import re
from typing import List, Optional

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


def find_best_matching_story_with_llm(message: str, stories: List[dict]) -> Optional[dict]:
    """
    Uses LLM to find the most appropriate matching story from a list.
    Returns None if no sufficiently strong match is found.
    """

    if not stories:
        return None

    indexed_stories = [f"{idx + 1}. {story['subject']}" for idx, story in enumerate(stories)]

    prompt = (
        "You're a project assistant. A new task has arrived from a team member.\n\n"
        "Here is the new task:\n"
        f"{message}\n\n"
        "Here are the available user stories (numbered):\n"
        + "\n".join(indexed_stories) + "\n\n"
        "Which ONE story does the new task most closely relate to?\n"
        "- Reply with the story NUMBER only (e.g., '2') if there's a clear match.\n"
        "- If no suitable match exists, reply with 'None'."
    )

    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        result = response.json().get("response", "").strip().lower()

        if result == "none":
            log.info("LLM responded: no matching story")
            return None

        if result.isdigit():
            index = int(result) - 1
            if 0 <= index < len(stories):
                matched_story = stories[index]
                log.info(f"LLM matched task to story: {matched_story['subject']}")
                return matched_story

        log.warning(f"LLM gave unexpected response: '{result}'")
        return None

    except requests.RequestException as e:
        log.error(f"LLM matching failed: {e}")
        return None


def check_duplicate_with_llm(new_task: str, existing_tasks: List[str]) -> Optional[str]:
    prompt = (
            "You are a task deduplication assistant. Your job is to determine if a task is a duplicate.\n"
            "Reply **only** with the exact duplicate task text from the list if it exists.\n"
            "Do not paraphrase or rephrase. Just return the exact match.\n"
            "Reply with 'None' if there is no duplicate.\n\n"
            f"New Task: {new_task}\n"
            "Existing Tasks:\n" + "\n".join(f"- {task}" for task in existing_tasks)
    )

    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=data)
        response.raise_for_status()
        result = response.json().get("response", "").strip()
        log.debug(f"LLM duplicate check result: {result}")

        match = re.search(r"\*\*(.*?)\*\*", result)
        if match:
            return match.group(1).strip()

        if "none" in result.lower():
            return None
        log.debug(f"LLM raw response for duplicate check: {result}")

        return result

    except requests.RequestException as e:
        log.error(f"Error communicating with Ollama LLM: {e}", HTTPStatus.INTERNAL_SERVER_ERROR)
        raise RuntimeError("Failed to enrich task using LLM")


def is_duplicate(task: str, existing_tasks: List[str], threshold: float = 0.5) -> bool:
    try:
        llm_result = check_duplicate_with_llm(task, existing_tasks)
        if llm_result:
            log.info(f"LLM detected duplicate for task: '{task}' ~ '{llm_result}'")
            return True
    except Exception as e:
        log.warning(f"LLM duplicate check failed. Falling back to fuzzy: {e}")

    for existing in existing_tasks:
        similarity = difflib.SequenceMatcher(None, task.lower(), existing.lower()).ratio()
        if similarity > threshold:
            log.info(f"Fallback duplicate task: '{task}' ~ '{existing}' (Similarity: {similarity:.2f})")
            return True

    return False


def is_duplicate_subtask(task: str, subtask_titles: List[str]) -> bool:
    try:
        log.debug(f"Checking LLM duplicate for sub-task: '{task}' in {subtask_titles}")
        llm_result = check_duplicate_with_llm(task, subtask_titles)
        log.debug(f"LLM result for sub-task duplicate check: {llm_result}")

        if llm_result:
            for existing in subtask_titles:
                if existing.strip().lower() == llm_result.strip().lower():
                    log.info(f"LLM detected confirmed duplicate sub-task: '{task}' ~ '{llm_result}'")
                    return True
            log.warning(f"LLM returned possible but unconfirmed match: '{llm_result}'")
    except Exception as e:
        log.warning(f"LLM sub-task duplicate check failed. Falling back to fuzzy: {e}")

    # Fallback fuzzy match with stricter threshold
    for existing in subtask_titles:
        similarity = difflib.SequenceMatcher(None, task.lower(), existing.lower()).ratio()
        if similarity > 0.7:
            log.info(f"Fallback fuzzy duplicate sub-task: '{task}' ~ '{existing}' (Similarity: {similarity:.2f})")
            return True

    return False

def choose_priority_with_llm(task_text: str, priorities: List[dict]) -> Optional[str]:
    priority_names = [p["name"] for p in priorities]
    prompt = (
        "You're a project assistant. Based on the task below, decide which of the following priorities is most suitable.\n\n"
        f"Task: {task_text}\n"
        f"Available Priorities: {', '.join(priority_names)}\n\n"
        "Reply only with the priority name (exactly as listed)."
    )

    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }, timeout=15)
        response.raise_for_status()
        result = response.json().get("response", "").strip()
        return result
    except Exception as e:
        log.error(f"Priority LLM failed: {e}")
        return None
