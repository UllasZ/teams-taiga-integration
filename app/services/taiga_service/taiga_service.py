from typing import List
from app.api_clients.taiga_client import (
    get_project_by_slug, get_user_stories, get_userstory_statuses,
    get_priorities, create_user_story, get_tasks_for_story,
    create_userstory_task, get_task_statuses
)
from app.config import TAIGA_PROJECT_SLUG
from app.logger.logger import log


def get_project_id() -> int:
    try:
        project = get_project_by_slug(TAIGA_PROJECT_SLUG)
        log.debug(f"Fetched project: {project['id']}")
        return project["id"]
    except Exception as e:
        log.error(f"Error fetching project by slug: {e}")
        raise


def get_all_user_stories() -> List[dict]:
    try:
        project_id = get_project_id()
        stories = get_user_stories(project_id)
        log.debug(f"Fetched {len(stories)} user stories")
        return stories
    except Exception as e:
        log.error(f"Error fetching user stories: {e}")
        raise


def get_all_sub_tasks(userstory_id: int) -> List[dict]:
    try:
        tasks = get_tasks_for_story(userstory_id)
        log.debug(f"Fetched {len(tasks)} tasks for story ID {userstory_id}")
        return tasks
    except Exception as e:
        log.error(f"Error fetching tasks for user story {userstory_id}: {e}")
        raise


def get_userstory_status(project_id: int) -> int:
    try:
        statuses = get_userstory_statuses(project_id)
        if not statuses:
            raise ValueError("No user story statuses found")
        log.debug(f"Using status: {statuses[0]}")
        return statuses[0]["id"]
    except Exception as e:
        log.error(f"Error fetching user story statuses: {e}")
        raise


def get_task_status(project_id: int) -> int:
    try:
        statuses = get_task_statuses(project_id)
        if not statuses:
            raise ValueError("No task statuses found")
        log.debug(f"Using task status: {statuses[0]}")
        return statuses[0]["id"]
    except Exception as e:
        log.error(f"Error fetching task statuses: {e}")
        raise


def get_priority_id(title: str, project_id: int, choose_priority_func) -> int:
    try:
        priorities = get_priorities(project_id)
        selected = choose_priority_func(title, priorities)
        match = next((p["id"] for p in priorities if p["name"].lower() == selected.lower()), None)
        if match is None:
            raise ValueError(f"No matching priority for '{selected}'")
        log.debug(f"Selected priority: {selected} → ID: {match}")
        return match
    except Exception as e:
        log.error(f"Error determining priority ID for title '{title}': {e}")
        raise


def create_user_story_entry(payload: dict) -> dict:
    try:
        log.debug(f"Creating user story with title: {payload['subject']}")
        return create_user_story(payload)
    except Exception as e:
        log.error(f"Error creating user story: {e}")
        raise


def create_user_story_task(userstory_id: int, payload: dict) -> dict:
    try:
        log.debug(f"Creating sub-task in story {userstory_id} with title: {payload['subject']}")
        return create_userstory_task(userstory_id, payload)
    except Exception as e:
        log.error(f"Error creating sub-task: {e}")
        raise
