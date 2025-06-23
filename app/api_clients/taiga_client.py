import requests
from app.config import TAIGA_API_URL
from app.logger.logger import log
from app.services.taiga_service.taiga_auth import get_taiga_token


def taiga_auth_headers():
    return {"Authorization": f"Bearer {get_taiga_token()}"}


def get_project_by_slug(slug: str) -> dict:
    try:
        url = f"{TAIGA_API_URL}/projects/by_slug?slug={slug}"
        response = requests.get(url, headers=taiga_auth_headers())
        response.raise_for_status()
        log.debug("Fetched project by slug")
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error fetching project: {e}")
        raise


def get_user_stories(project_id: int) -> list:
    try:
        url = f"{TAIGA_API_URL}/userstories?project={project_id}"
        response = requests.get(url, headers=taiga_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error fetching user stories: {e}")
        raise


def get_userstory_statuses(project_id: int) -> list:
    try:
        url = f"{TAIGA_API_URL}/userstory-statuses?project={project_id}"
        response = requests.get(url, headers=taiga_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error fetching user story statuses: {e}")
        raise


def get_task_statuses(project_id: int) -> list:
    try:
        url = f"{TAIGA_API_URL}/task-statuses?project={project_id}"
        response = requests.get(url, headers=taiga_auth_headers())
        response.raise_for_status()
        log.debug("Fetched task statuses")
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error fetching task statuses: {e}")
        raise


def create_user_story(payload: dict) -> dict:
    try:
        response = requests.post(
            f"{TAIGA_API_URL}/userstories",
            json=payload,
            headers=taiga_auth_headers(),
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error creating user story: {e}")
        raise


def get_tasks_for_story(story_id: int) -> list[dict]:
    try:
        url = f"{TAIGA_API_URL}/tasks?user_story={story_id}"
        response = requests.get(url, headers=taiga_auth_headers())
        response.raise_for_status()
        log.debug(f"Fetched tasks for story ID {story_id}")
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error fetching tasks for story {story_id}: {e}")
        raise


def create_task(payload: dict) -> dict:
    try:
        response = requests.post(
            f"{TAIGA_API_URL}/tasks",
            json=payload,
            headers=taiga_auth_headers()
        )
        response.raise_for_status()
        log.info(f"Sub-task created under story {payload.get('user_story')}")
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error creating sub-task: {e}")
        raise


def create_userstory_task(userstory_id: int, payload: dict) -> dict:
    try:
        payload["user_story"] = userstory_id
        response = requests.post(
            f"{TAIGA_API_URL}/tasks",
            json=payload,
            headers=taiga_auth_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error creating sub-task: {e}")
        raise

def get_priorities(project_id: int) -> list[dict]:
    try:
        url = f"{TAIGA_API_URL}/priorities?project={project_id}"
        response = requests.get(url, headers=taiga_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error getting priorities: {e}")
        raise
