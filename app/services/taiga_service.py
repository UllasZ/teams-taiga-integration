from typing import List

from app.api_clients.taiga_client import (
    get_project_by_slug,
    get_user_stories,
    get_userstory_statuses,
    create_user_story,
    get_task_statuses,
    create_userstory_task,
    get_tasks_for_story,
    get_priorities
)
from app.config import TAIGA_PROJECT_SLUG
from app.logger.logger import log
from app.services.llm_service import (
    find_best_matching_story_with_llm,
    check_duplicate_with_llm,
    is_duplicate_subtask,
    enrich_task_with_llm,
    choose_priority_with_llm
)


def get_project_id() -> int:
    return get_project_by_slug(TAIGA_PROJECT_SLUG)["id"]


def get_all_user_stories() -> List[dict]:
    project_id = get_project_id()
    return get_user_stories(project_id)


def get_subtask_titles(userstory_id: int) -> List[str]:
    try:
        tasks = get_tasks_for_story(userstory_id)
        log.debug(f"Sub-tasks for story {userstory_id}: {[t['subject'] for t in tasks]}")
        return [task["subject"] for task in tasks if "subject" in task]
    except Exception as e:
        log.error(f"Error fetching sub-task titles: {e}")
        return []

def get_priority_id(title, project_id):
    # Priority logic
    priorities = get_priorities(project_id)
    selected_name = choose_priority_with_llm(title, priorities)
    priority_id = next((p["id"] for p in priorities if p["name"].lower() == selected_name.lower()), None)
    return priority_id

def create_taiga_task(title: str) -> dict:
    project_id = get_project_id()
    statuses = get_userstory_statuses(project_id)
    if not statuses:
        raise ValueError("No statuses found")

    description = enrich_task_with_llm(title)
    priority_id = get_priority_id(title, project_id)

    payload = {
        "project": project_id,
        "subject": title,
        "description": description,
        "description_html": f"<p>{description}</p>",
        "status": statuses[0]["id"],
        "priority": priority_id,
        "version": 1
    }

    return create_user_story(payload)


def create_sub_task(userstory_id: int, title: str) -> dict:
    project_id = get_project_id()
    task_statuses = get_task_statuses(project_id)
    if not task_statuses:
        raise ValueError("No task statuses found")

    description = enrich_task_with_llm(title)
    priority_id = get_priority_id(title, project_id)

    payload = {
        "subject": title,
        "project": project_id,
        "status": task_statuses[0]["id"],
        "description": description,
        "description_html": f"<p>{description}</p>",
        "priority": priority_id  # ✅ Added
    }

    return create_userstory_task(userstory_id, payload)


def handle_teams_webhook_message(message: str) -> dict:
    try:
        message = message.strip()
        if not message:
            return {"message": "Empty message. Skipping."}

        stories = get_all_user_stories()
        story_titles = [s["subject"] for s in stories]

        # Check if this is a duplicate story
        matched_story_title = check_duplicate_with_llm(message, story_titles)
        if matched_story_title:
            matched_story = next(
                (s for s in stories if s["subject"].strip().lower() == matched_story_title.strip().lower()), None
            )

            if matched_story:
                log.info(f"LLM confirmed story match: '{message}' ~ '{matched_story_title}'")

                # Check for duplicate sub-task under the matched story
                subtask_titles = get_subtask_titles(matched_story["id"])
                duplicate_subtask = check_duplicate_with_llm(message, subtask_titles)
                if duplicate_subtask:
                    log.info(f"LLM confirmed duplicate sub-task: '{message}' ~ '{duplicate_subtask}'")
                    return {"message": "Duplicate sub-task. Skipping."}

                # Create sub-task if no duplicate found
                created_subtask = create_sub_task(matched_story["id"], message)
                return {"message": "Sub-task created", "subtask": created_subtask}

        # If no matching story, check semantically and assign it
        parent_story = find_best_matching_story_with_llm(message, stories)
        if parent_story:
            log.info(f"LLM found best match story (semantic): {parent_story['subject']}")
            subtask_titles = get_subtask_titles(parent_story["id"])
            if is_duplicate_subtask(message, subtask_titles):
                return {"message": "Duplicate sub-task under story. Skipping."}
            created_subtask = create_sub_task(parent_story["id"], message)
            return {"message": "Sub-task created", "subtask": created_subtask}

        # No story match at all, create new user story
        new_story = create_taiga_task(message)
        return {"message": "New user story created", "story": new_story}

    except Exception as e:
        log.error(f"Webhook error: {str(e)}")
        return {"message": "Error processing webhook", "error": str(e)}
