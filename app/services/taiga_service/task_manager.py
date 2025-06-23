
from app.logger.logger import log
from app.services.llm_service.llm_service import enrich_task_description, choose_priority, classify_prompt
from app.services.taiga_service.taiga_service import get_project_id, get_userstory_status, get_priority_id, \
    create_user_story_entry, get_task_status, create_user_story_task, get_all_user_stories, get_all_sub_tasks


def create_taiga_task(title: str) -> dict:
    try:
        project_id = get_project_id()
        status_id = get_userstory_status(project_id)
        description = enrich_task_description(title)
        priority_id = get_priority_id(title, project_id, choose_priority)

        payload = {
            "project": project_id,
            "subject": title,
            "description": description,
            "description_html": f"<p>{description}</p>",
            "status": status_id,
            "priority": priority_id,
            "version": 1
        }

        log.info(f"Creating new user story: {title}")
        return create_user_story_entry(payload)
    except Exception as e:
        log.error(f"Failed to create user story for '{title}': {e}")
        raise


def create_sub_task(userstory_id: int, title: str) -> dict:
    try:
        project_id = get_project_id()
        status_id = get_task_status(project_id)
        description = enrich_task_description(title)
        priority_id = get_priority_id(title, project_id, choose_priority)

        payload = {
            "subject": title,
            "project": project_id,
            "status": status_id,
            "description": description,
            "description_html": f"<p>{description}</p>",
            "priority": priority_id
        }

        log.info(f"Creating sub-task '{title}' under story {userstory_id}")
        return create_user_story_task(userstory_id, payload)
    except Exception as e:
        log.error(f"Failed to create sub-task '{title}' under story {userstory_id}: {e}")
        raise


def handle_teams_message(message: str):
    try:
        message = message.strip()
        if not message:
            log.info("Empty message received. Skipping.")
            return {"message": "Empty message. Skipping."}

        log.info(f"Processing Teams message: '{message}'")
        stories = get_all_user_stories()
        existing_stories = [(s['id'], s['subject']) for s in stories]
        duplicate = classify_prompt(message, existing_stories)

        if duplicate is None:
            story = create_taiga_task(message)
            log.info(f"Created new user story: {story.get('subject')}")
            return {"message": "New story created", "story": message}

        elif duplicate.startswith("D"):
            original = duplicate[1:]
            log.info(f"Detected duplicate story. Incoming: '{message}' ~ Existing: '{original}'")
            return {"message": "Duplicate story. Skipping."}

        elif duplicate.startswith("S"):
            story_id = int(duplicate[1:])
            sub_tasks = get_all_sub_tasks(story_id)
            existing_subs = [(s['id'], s['subject']) for s in sub_tasks]
            duplicate_sub = classify_prompt(message, existing_subs)

            if duplicate_sub is None:
                sub_task = create_sub_task(story_id, message)
                log.info(f"Created new sub-task '{sub_task.get('subject')}' under story {story_id}")
                return {"message": "New sub-task created", "story": story_id, "sub-task": message}
            else:
                log.info(f"Detected duplicate sub-task. Incoming: '{message}' ~ Existing: '{duplicate_sub[1:]}'")
                return {"message": "Duplicate sub-task. Skipping."}

    except Exception as e:
        log.error(f"Error processing message '{message}': {e}")
        return {"message": f"Internal error processing task: {e}"}
