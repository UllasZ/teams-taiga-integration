import requests
from app.config import TAIGA_API_URL
from app.services.taiga_auth import get_taiga_token
from app.logger.logger import log


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
        log.error(f"Error fetching statuses: {e}")
        raise


def create_user_story(payload: dict) -> dict:
    try:
        response = requests.post(
            f"{TAIGA_API_URL}/userstories",
            json=payload,
            headers=taiga_auth_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Error creating user story: {e}")
        raise
