from typing import List, Optional

from app.api_clients.llm_client import call_llm
from app.logger.logger import log


def enrich_task_description(title: str) -> str:
    """Generate a concise enriched description for a task title using LLM."""
    prompt = (
        "You are a project assistant. Based on the following task title, "
        "write a clear, concise task description in 2-3 sentences.\n"
        f"Task title: {title}"
    )
    return call_llm(prompt)

def choose_priority(task_text: str, priorities: List[dict]) -> Optional[str]:
    """Let LLM choose the most relevant priority from list based on task."""
    names = [p["name"] for p in priorities]
    prompt = (
        "You're a project assistant. Based on the task below, decide the best priority.\n\n"
        f"Task: {task_text}\n"
        f"Available Priorities: {', '.join(names)}\n\n"
        "Reply only with the exact priority name."
    )

    try:
        result = call_llm(prompt)
        return result if result in names else None
    except Exception as e:
        log.error(f"LLM failed to choose priority: {e}")
        return None

def classify_prompt(message: str, existing_stories: list[tuple[str, str]]) -> str:
    normalized_message = message.strip().lower()

    for story_id, story_text in existing_stories:
        normalized_story = story_text.strip().lower()
        if normalized_message == normalized_story:
            return f"D{story_id}"  # Exact match
        elif normalized_message in normalized_story or normalized_story in normalized_message:
            return f"S{story_id}"  # Partial string match

    return ask_ollama_for_similarity(message, existing_stories)

def ask_ollama_for_similarity(message, existing_stories):
    if not existing_stories:
        return None

    prompt = (
            "You are a story deduplication assistant. Your job is to determine if the new message is a duplicate or similar to one of the existing stories. "
            "\n\nRespond with:"
            "\n- D<story_id> if the new message is an exact match of an existing story."
            "\n- S<story_id> if the new message is similar (but not exactly the same) to an existing story."
            "\n- None if there is no match at all."
            f"\n\nNew Prompt: {message}\n"
            "Existing Stories:\n" + "\n".join(f"{story[0]} - {story[1]}" for story in existing_stories)
    )

    try:
        result = call_llm(prompt).strip()
        log.debug(f"Raw LLM duplicate check result: '{result}'")

        if result.lower() == "none":
            return None

        # Normalize and check for match in existing_tasks
        for original in existing_stories:
            if result.lower() == original.lower():
                # Return original for consistent casing
                return original

        log.warning(f"LLM response '{result}' not found in existing tasks.")
        return None

    except Exception as e:
        log.error(f"Error during LLM duplicate check: {e}")
        return None


