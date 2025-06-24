from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import teams

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 Mount your Teams router with the /teams prefix
app.include_router(teams.router, prefix="/teams")
