from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api_clients.taiga_client import get_user_story_by_id, get_task_by_id
from app.logger.logger import log
from app.services.taiga_service.taiga_service import get_all_user_stories, get_all_sub_tasks
from app.services.taiga_service.task_manager import handle_teams_message

router = APIRouter()

class TeamsMessage(BaseModel):
    message: str

@router.post("/simulate")
def process_teams_message(payload: TeamsMessage):
    try:
        result = handle_teams_message(payload.message)
        return result

    except Exception as e:
        log.error(f"Error handling teams simulate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/user_stories")
def get_user_stories():
    try:
        result = get_all_user_stories()
        return result

    except Exception as e:
        log.error(f"Error handling User stories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/user_stories/{story_id}")
def get_user_story(story_id):
    try:
        result = get_user_story_by_id(story_id)
        return result

    except Exception as e:
        log.error(f"Error handling User story: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user_stories/{story_id}/tasks")
def get_user_story_tasks(story_id):
    try:
        result = get_all_sub_tasks(story_id)
        return result

    except Exception as e:
        log.error(f"Error handling User story tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/tasks/{task_id}")
def get_user_story_task(task_id):
    try:
        result = get_task_by_id(task_id)
        return result

    except Exception as e:
        log.error(f"Error handling User story tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
