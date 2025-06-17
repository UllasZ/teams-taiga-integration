from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from app.logger.logger import log
from app.services.taiga_service import get_existing_taiga_tasks, is_duplicate, create_taiga_task
from app.services.llm_service import enrich_task_with_llm
from app.services.teams_service import mock_create_team, get_mock_team_by_task_id

router = APIRouter()

# Webhook from Teams message
@router.post("/")
async def teams_webhook(request: Request):
    try:
        body = await request.json()
        message = body.get("text", "").strip()

        log.info(f"Received Teams message: {message}")

        existing_tasks = get_existing_taiga_tasks()
        if is_duplicate(message, existing_tasks):
            log.info(f"Duplicate task detected from Teams: {message}")
            return {"status": "duplicate", "message": "Task already exists"}

        description = enrich_task_with_llm(message)
        task = create_taiga_task(message, description)

        log.info(f"Task created via Teams webhook: {task['id']}")
        return {"status": "created", "task": task}
    except Exception as e:
        log.error(f"Teams webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Mocked team creation only
class TeamCreateRequest(BaseModel):
    name: str
    description: str = ""

@router.post("/mock-create")
def mock_create_team_route(data: TeamCreateRequest):
    try:
        log.info(f"Creating mock team: {data.name}")
        result = mock_create_team(data.name, data.description)
        return {"message": "Team mock created", "team": result}
    except Exception as e:
        log.error(f"Mock team creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Create task and link to mock team
class TaskWithTeamRequest(BaseModel):
    title: str
    description: str = ""
    team_name: str
    team_description: str = ""

@router.post("/create-task-with-team")
def create_task_and_mock_team(data: TaskWithTeamRequest):
    try:
        log.info(f"Received request to create task and team: {data.title} → {data.team_name}")
        existing_tasks = get_existing_taiga_tasks()
        if is_duplicate(data.title, existing_tasks):
            log.info(f"Duplicate task: {data.title}")
            return {"status": "duplicate", "message": "Task already exists"}

        final_description = data.description or enrich_task_with_llm(data.title)
        task = create_taiga_task(data.title, final_description)

        team = mock_create_team(
            team_name=data.team_name,
            description=data.team_description,
            taiga_task_id=task["id"]
        )

        log.info(f"Created task {task['id']} and linked mock team '{data.team_name}'")
        return {
            "message": "Taiga task and mock Teams team created",
            "task": task,
            "mock_team": team
        }
    except Exception as e:
        log.error(f"Failed to create task and team: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Get linked team for a task
@router.get("/team-by-task/{task_id}")
def get_team_by_task(task_id: int):
    try:
        log.info(f"Fetching linked team for task {task_id}")
        team = get_mock_team_by_task_id(task_id)
        if team:
            return {"linked_team": team}
        log.info(f"No linked team for task {task_id}")
        raise HTTPException(status_code=404, detail="No team linked to this task")
    except Exception as e:
        log.error(f"Error fetching team for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Create and link mock Team for existing task
class TeamWithTaskIDRequest(BaseModel):
    team_name: str
    description: str = ""
    taiga_task_id: int

@router.post("/create-team")
def create_and_link_team(data: TeamWithTaskIDRequest):
    try:
        log.info(f"Linking team '{data.team_name}' to task {data.taiga_task_id}")
        team = mock_create_team(
            team_name=data.team_name,
            description=data.description,
            taiga_task_id=data.taiga_task_id
        )
        return {"message": "Mock team created and linked", "team": team}
    except Exception as e:
        log.error(f"Failed to create and link team: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
