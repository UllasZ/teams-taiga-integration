import requests
from app.config import TAIGA_API_URL, TAIGA_USERNAME, TAIGA_PASSWORD
from app.logger.logger import log

_token_cache = {"token": None}

def get_taiga_token():
    if _token_cache["token"]:
        log.debug("Using cached Taiga token")
        return _token_cache["token"]

    try:
        log.info("Requesting new Taiga auth token...")
        response = requests.post(
            f"{TAIGA_API_URL}/auth",
            json={
                "type": "normal",
                "username": TAIGA_USERNAME,
                "password": TAIGA_PASSWORD
            }
        )
        response.raise_for_status()
        token = response.json()["auth_token"]
        _token_cache["token"] = token
        log.info("Taiga auth token acquired successfully")
        return token

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to authenticate with Taiga: {e}")
        raise RuntimeError("Unable to authenticate with Taiga API")
