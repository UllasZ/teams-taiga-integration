from fastapi import FastAPI
from app.api.teams import router as teams_router

app = FastAPI()

app.include_router(teams_router, prefix="/teams", tags=["Teams Webhook"])
