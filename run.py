from fastapi import FastAPI, Request, HTTPException
import os

from app.services.llm_service import enrich_task_with_llm
from app.services.taiga_service import get_existing_taiga_tasks, is_duplicate, create_taiga_task

app = FastAPI()

TEAMS_SECRET = os.getenv("TEAMS_SECRET")

@app.post("/teams")
async def teams_webhook(request: Request):
    body = await request.json()

    if body.get("token") != TEAMS_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Teams token")

    message = body.get("text", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="No message text provided")

    existing_tasks = get_existing_taiga_tasks()
    if is_duplicate(message, [task['subject'] for task in existing_tasks]):
        return {"status": "duplicate", "message": "Task already exists"}

    description = enrich_task_with_llm(message)
    task = create_taiga_task(message, description)
    return {"status": "created", "task_id": task['id'], "title": task['subject']}
