from typing import List
import difflib

from app.api_clients.taiga_client import (
    get_project_by_slug,
    get_user_stories,
    get_userstory_statuses,
    create_user_story,
)
from app.config import TAIGA_PROJECT_SLUG
from app.logger.logger import log


def get_project_id() -> int:
    return get_project_by_slug(TAIGA_PROJECT_SLUG)["id"]


def get_existing_taiga_tasks() -> List[str]:
    project_id = get_project_id()
    stories = get_user_stories(project_id)
    return [story["subject"] for story in stories]


def is_duplicate(task: str, existing_tasks: List[str]) -> bool:
    for existing in existing_tasks:
        similarity = difflib.SequenceMatcher(None, task.lower(), existing.lower()).ratio()
        if similarity > 0.8:
            log.info(f"Duplicate task detected: '{task}' ~ '{existing}' (Similarity: {similarity:.2f})")
            return True
    return False


def create_taiga_task(title: str, description: str) -> dict:
    project_id = get_project_id()
    statuses = get_userstory_statuses(project_id)
    if not statuses:
        raise ValueError("No statuses found")

    payload = {
        "project": project_id,
        "subject": title,
        "description": description,
        "description_html": f"<p>{description}</p>",
        "status": statuses[0]["id"],
        "version": 1
    }

    return create_user_story(payload)
