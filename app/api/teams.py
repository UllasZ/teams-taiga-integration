# app/api/teams_webhook.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.taiga_service import handle_teams_webhook_message

router = APIRouter()

class TeamsMessage(BaseModel):
    text: str

@router.post("/webhook")
def process_teams_message(payload: TeamsMessage):
    result = handle_teams_webhook_message(payload.text)
    return result

