import os
from dotenv import load_dotenv

load_dotenv()

TAIGA_API_URL = "https://api.taiga.io/api/v1"
TAIGA_PROJECT_SLUG = os.getenv("TAIGA_PROJECT_SLUG")

TAIGA_USERNAME = os.getenv("TAIGA_USERNAME")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")