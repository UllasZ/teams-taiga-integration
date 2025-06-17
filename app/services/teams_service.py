import uuid
from typing import List, Optional
from app.logger.logger import log

# In-memory store
mock_teams: List[dict] = []

def mock_create_team(team_name: str, description: str = "", taiga_task_id: int = None) -> dict:
    try:
        team = {
            "team_id": str(uuid.uuid4()),
            "team_name": team_name,
            "description": description,
            "linked_taiga_task_id": taiga_task_id,
            "primary_channel": {
                "channel_id": str(uuid.uuid4()),
                "channel_name": "General"
            },
            "status": "mock_created"
        }

        mock_teams.append(team)
        log.info(f"Mock team '{team_name}' created and linked to task_id={taiga_task_id}")
        return team

    except Exception as e:
        log.error(f"Error creating mock team '{team_name}': {e}")
        raise


def get_mock_team_by_task_id(task_id: int) -> Optional[dict]:
    try:
        for team in mock_teams:
            if team.get("linked_taiga_task_id") == task_id:
                log.debug(f"Found mock team for task_id={task_id}")
                return team
        log.info(f"No team linked to task_id={task_id}")
        return None
    except Exception as e:
        log.error(f"Error retrieving team by task_id={task_id}: {e}")
        raise
