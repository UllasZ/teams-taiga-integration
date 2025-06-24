# Teams to Taiga Integration (with LLM support)
This project demonstrates a simple mock integration between Microsoft Teams and Taiga, where a Teams message (mocked via an API) creates a task in Taiga. The task is enriched using a local LLM (Llama3 via Ollama). It's designed as a take-home interview assessment and uses FastAPI for the API layer, with proper separation of concerns across routers, services, and API clients.

## Features
- Create Taiga tasks based on simulated Teams messages
- Automatically generate descriptions using a local LLM
- Avoid duplicate task creation using fuzzy matching
- Mock creation of Microsoft Teams team and channels
- Link Teams teams to Taiga tasks
- Centralized logging to file
- Clean, testable, extensible architecture

## Workflow Summary
- Message is sent via /simulate.
- Existing user stories and sub-tasks are fetched from Taiga.
- Semantic comparison avoids duplicate creation.
- LLM generates description and sub-tasks.
- Task is created under matched or new story in Taiga.

## Project Structure
```bash
.
├── api/
│   └── teams.py                 # Simulated Microsoft Teams webhook & task linking endpoints
│
├── app/
│   ├── api_clients/
│   │   ├── llm_client.py        # Raw HTTP client for communicating with Ollama LLM API
│   │   └── taiga_client.py      # Raw HTTP client for interacting with Taiga API (e.g., auth, task ops)
│   │
│   ├── logger/
│   │   └── logger.py            # Custom logger setup using Python's logging module, logs to files
│   │
│   ├── services/
│   │   ├── llm_service/
│   │   │   └── llm_service.py   # Business logic for calling Ollama to enhance task descriptions
│   │   │
│   │   └── taiga_service/
│   │       ├── taiga_auth.py    # Handles Taiga authentication and token management
│   │       ├── taiga_service.py # Abstracts high-level operations (fetch/create tasks, projects)
│   │       └── task_manager.py  # Orchestrates task creation logic: duplication check, hierarchy, etc.
│   │
│   ├── utils/
│   │   └── utils.py             # Stateless helper functions; no external dependencies
│   │
│   ├── config.py                # Centralized environment/config variable loader
│   └── main.py                  # FastAPI app entrypoint with route registration
│
├── logs/                        # Directory for storing generated log files
├── .gitignore                   # Specifies intentionally untracked files to ignore
├── README.md                    # Project documentation
└── run.py                       # Optional startup script for launching the application
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/teams-taiga-integration.git
cd teams-taiga-integration
```

### 2. Install dependencies
Make sure Poetry is installed on your system. Then run:
```bash
poetry install
```

### 3. Create a .env file
Inside the root directory, create a .env file with the following variables:
```bash
TAIGA_API_URL=https://api.taiga.io/api/v1
TAIGA_USERNAME=your_taiga_username
TAIGA_PASSWORD=your_taiga_password
TAIGA_PROJECT_SLUG=your-project-slug
OLLAMA_API_URL=http://localhost:11434/api/generate
```

### 4. Run Ollama locally
Ensure you have Ollama installed and running:
```bash
ollama run llama3
```
This should expose the model at http://localhost:11434.

### 5. Start the FastAPI server
```bash
poetry run uvicorn main:app --reload
```
This will start the server at http://127.0.0.1:8000.

## API Endpoints
### POST /teams/simulate
Simulate a Teams message.
```bash
curl -X POST http://127.0.0.1:8000/teams/simulate \
     -H "Content-Type: application/json" \
     -d '{"message": "The reports page is failing on mobile."}'
```
## GET /teams/user_stories
Returns all user stories in the project.

## GET /teams/user_stories/{story_id}
Returns a specific user story by ID.

## GET /teams/user_stories/{story_id}/tasks
Returns all tasks (sub-tasks) under a specific user story.

## GET /teams/tasks/{task_id}
Returns a specific sub-task by ID.

### Logs
Logs are saved in the logs/teams_taiga_integration.log file. Logging includes:
- Task creation events
- Duplicate detection
- LLM enrichment calls
- Errors from Taiga or Ollama

### API Testing with Insomnia
- Open Insomnia.
- Import raw JSON:
```bash
{
  "message": "We need a CI/CD pipeline for our microservices"
}
```
- Send a POST request to ```bash /teams/simulate```.

### Notes
- This project is a mock and does not interact with real Teams APIs.
- All team/channel logic is in-memory and not persisted.
- No caching is added in this version.
- Unit tests are not included.
- Priorities are fetched using:
  ```bash
  GET /api/v1/priorities?project=<project_id>
  ```
- Description content is enriched using an LLM. 
- Handles empty or irrelevant input gracefully.
- Duplicates are avoided using semantic similarity logic.

### Future Enhancements
- Add real Teams OAuth & webhook support
- Async background processing (LLM, Taiga I/O)
- Use Redis/DB for state persistence
- Token refresh logic for Taiga
- Unit & integration tests

## Frontend (React)
- Check out the dashboard frontend: https://github.com/UllasZ/teams-taiga-dashboard

- It includes:
  - Message Simulator UI
  - Live updates of stories and tasks
  - Chakra UI for components
  - Toast-based alerts instead of raw alerts

## This project is intended to show practical API design, async logic (where relevant), and clean code structure. Built for learning and demonstration purposes.