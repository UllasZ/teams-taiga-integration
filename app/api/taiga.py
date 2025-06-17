from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.logger.logger import log
from app.services.taiga_service import create_taiga_task, get_existing_taiga_tasks, is_duplicate

router = APIRouter()

class TaskCreateRequest(BaseModel):
    title: str
    description: str

@router.post("/create-task")
def create_task(request: TaskCreateRequest):
    try:
        log.info(f"Received task creation request: {request.title}")

        existing_tasks = get_existing_taiga_tasks()

        if is_duplicate(request.title, existing_tasks):
            log.info(f"Duplicate task detected: {request.title}")
            return {"message": "Duplicate task detected. Skipping creation."}

        created_task = create_taiga_task(request.title, request.description)

        log.info(f"Task created successfully: {created_task.get('id')}")
        return {"message": "Task created", "task": created_task}

    except Exception as e:
        log.error(f"Error while creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
