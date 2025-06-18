from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.logger.logger import log
from app.services.taiga_service import handle_teams_webhook_message

router = APIRouter()


class TeamsWebhookPayload(BaseModel):
    message: str


@router.post("/teams-webhook")
def handle_teams_webhook(payload: TeamsWebhookPayload):
    try:
        log.info(f"Received Teams webhook message: {payload.message}")
        result = handle_teams_webhook_message(payload.message)

        return {
            "message": result["message"],
            "type": result.get("type"),
            "task": result.get("task")
        }

    except Exception as e:
        log.error(f"Error handling Teams webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
