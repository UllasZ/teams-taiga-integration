import difflib
from typing import List, Optional
import requests
from http import HTTPStatus

from app.config import OLLAMA_API_URL
from app.logger.logger import log


def _call_llm(prompt: str, model: str = "llama3", timeout: int = 15) -> str:
    """Internal helper to send a prompt to the LLM and return the response text."""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        log.debug(f"LLM response: {response.status_code} - {response.text}")
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as e:
        log.error(f"Error communicating with Ollama LLM: {e}", HTTPStatus.INTERNAL_SERVER_ERROR)
        raise RuntimeError("Failed to communicate with LLM")


def enrich_task_with_llm(title: str) -> str:
    """Generate a concise enriched description for a task title using LLM."""
    prompt = (
        "You are a project assistant. Based on the following task title, "
        "write a clear, concise task description in 2-3 sentences.\n"
        f"Task title: {title}"
    )
    return _call_llm(prompt)


def find_best_matching_story_with_llm(message: str, stories: List[dict]) -> Optional[dict]:
    """Use LLM to find the best matching user story for a message."""
    if not stories:
        return None

    indexed = [f"{i+1}. {s['subject']}" for i, s in enumerate(stories)]
    prompt = (
        "You're a project assistant. A new task has arrived from a team member.\n\n"
        f"Task: {message}\n\n"
        "Available user stories:\n" + "\n".join(indexed) + "\n\n"
        "Which ONE story best matches the task?\n"
        "- Reply with the story NUMBER only (e.g., '2') if matched.\n"
        "- Reply 'None' if no suitable match exists."
    )

    result = _call_llm(prompt).strip().lower()
    log.debug(f"LLM response for story match: '{result}'")

    if result == "none":
        log.info("LLM: No suitable matching story.")
        return None

    # Accept only single valid integer values
    if result.isdigit():
        index = int(result) - 1
        if 0 <= index < len(stories):
            matched = stories[index]
            log.info(f"LLM matched task to story: {matched['subject']}")
            return matched

    log.warning(f"LLM gave unexpected story match output: '{result}' — treating as no match.")
    return None


def check_duplicate_with_llm(new_task: str, existing_tasks: List[str]) -> Optional[str]:
    """Use LLM to determine if the new task is a duplicate of any existing task."""
    if not existing_tasks:
        return None

    prompt = (
        "You are a task deduplication assistant. Your job is to determine if the new task "
        "is a duplicate of one of the existing tasks.\n"
        "Reply ONLY with the exact duplicate task text from the list.\n"
        "Reply with 'None' if no duplicate exists.\n\n"
        f"New Task: {new_task}\n"
        "Existing Tasks:\n" + "\n".join(f"- {task}" for task in existing_tasks)
    )

    try:
        result = _call_llm(prompt).strip()
        log.debug(f"Raw LLM duplicate check result: '{result}'")

        if result.lower() == "none":
            return None

        # Normalize and check for match in existing_tasks
        for original in existing_tasks:
            if result.lower() == original.lower():
                return original  # Return original for consistent casing

        log.warning(f"LLM response '{result}' not found in existing tasks.")
        return None

    except Exception as e:
        log.error(f"Error during LLM duplicate check: {e}")
        return None


def is_duplicate(task: str, existing_tasks: List[str], threshold: float = 0.5) -> bool:
    """Check if task is a duplicate using LLM and fuzzy fallback."""
    try:
        llm_result = check_duplicate_with_llm(task, existing_tasks)
        if llm_result:
            log.info(f"LLM duplicate: '{task}' ~ '{llm_result}'")
            return True
    except Exception as e:
        log.warning(f"LLM duplicate check failed, using fallback: {e}")

    for existing in existing_tasks:
        similarity = difflib.SequenceMatcher(None, task.lower(), existing.lower()).ratio()
        if similarity > threshold:
            log.info(f"Fuzzy duplicate: '{task}' ~ '{existing}' (Similarity: {similarity:.2f})")
            return True

    return False


def is_duplicate_subtask(task: str, subtask_titles: List[str]) -> bool:
    """Check for sub-task duplication using LLM and stricter fuzzy fallback."""
    try:
        log.debug(f"LLM check: is sub-task '{task}' a duplicate of any in: {subtask_titles}")
        llm_result = check_duplicate_with_llm(task, subtask_titles)

        if llm_result:
            log.debug(f"LLM returned for duplicate check: '{llm_result}'")
            for original in subtask_titles:
                if llm_result.strip().lower() == original.strip().lower():
                    log.info(f"Confirmed duplicate sub-task via LLM: '{task}' ~ '{original}'")
                    return True

            log.warning(f"LLM returned a value not found in existing sub-tasks: '{llm_result}'")
    except Exception as e:
        log.warning(f"LLM sub-task duplicate check failed. Using fallback: {e}")

    # Fallback: Fuzzy match
    for existing in subtask_titles:
        similarity = difflib.SequenceMatcher(None, task.lower(), existing.lower()).ratio()
        if similarity > 0.7:
            log.info(f"Fuzzy duplicate sub-task: '{task}' ~ '{existing}' (Similarity: {similarity:.2f})")
            return True

    return False


def choose_priority_with_llm(task_text: str, priorities: List[dict]) -> Optional[str]:
    """Let LLM choose the most relevant priority from list based on task."""
    names = [p["name"] for p in priorities]
    prompt = (
        "You're a project assistant. Based on the task below, decide the best priority.\n\n"
        f"Task: {task_text}\n"
        f"Available Priorities: {', '.join(names)}\n\n"
        "Reply only with the exact priority name."
    )

    try:
        result = _call_llm(prompt)
        return result if result in names else None
    except Exception as e:
        log.error(f"LLM failed to choose priority: {e}")
        return None
