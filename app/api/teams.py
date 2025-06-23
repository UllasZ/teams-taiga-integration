from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.logger.logger import log
from app.services.taiga_service.task_manager import handle_teams_message

router = APIRouter()

class TeamsMessage(BaseModel):
    text: str

@router.post("/webhook")
def process_teams_message(payload: TeamsMessage):
    try:
        result = handle_teams_message(payload.text)
        return result

    except Exception as e:
        log.error(f"Error handling Teams webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
