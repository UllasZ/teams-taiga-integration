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
        "priority": priority_id
    }

    return create_userstory_task(userstory_id, payload)


def handle_teams_webhook_message(message: str) -> dict:
    try:
        message = message.strip()
        if not message:
            return {"message": "Empty message. Skipping."}

        # Step 1: Get all stories for the project
        stories = get_all_user_stories()
        story_titles = [s["subject"] for s in stories]

        # Step 2: Check if the message is a duplicate of any story
        duplicate_story_title = check_duplicate_with_llm(message, story_titles)
        if duplicate_story_title:
            matched_story = next(
                (s for s in stories if s["subject"].strip().lower() == duplicate_story_title.strip().lower()), None
            )
            if matched_story:
                subtask_titles = get_subtask_titles(matched_story["id"])
                duplicate_subtask = check_duplicate_with_llm(message, subtask_titles)
                if duplicate_subtask:
                    log.info(f"Duplicate sub-task: '{message}' ~ '{duplicate_subtask}'")
                    return {"message": "Duplicate sub-task. Skipping."}

                created_subtask = create_sub_task(matched_story["id"], message)
                return {"message": "Sub-task created under exact story match", "subtask": created_subtask}

        # Step 3: Try to find a best matching story (fuzzy match)
        best_match = find_best_matching_story_with_llm(message, stories)
        if best_match:
            log.info(f"LLM suggested matching story: {best_match['subject']}")
            subtask_titles = get_subtask_titles(best_match["id"])

            # Check if it's already a sub-task
            if is_duplicate_subtask(message, subtask_titles):
                return {"message": "Duplicate sub-task (fuzzy match). Skipping."}

            created_subtask = create_sub_task(best_match["id"], message)
            return {"message": "Sub-task created under fuzzy-matched story", "subtask": created_subtask}

        # Step 4: No match at all → create a new user story
        created_user_story = create_taiga_task(message)
        return {"message": "No match found. New user story created", "user_story": created_user_story}

    except Exception as e:
        log.error(f"Error handling Teams message: {e}")
        return {"message": f"Internal error processing task: {e}"}
