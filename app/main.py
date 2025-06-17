from fastapi import FastAPI

from app.api import taiga
from app.api.teams import router as teams_router

app = FastAPI()

app.include_router(teams_router, prefix="/teams", tags=["Teams Webhook"])
app.include_router(taiga.router, prefix="/taiga", tags=["Taiga"])
