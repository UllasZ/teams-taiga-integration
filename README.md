# Teams to Taiga Integration (with LLM support)

This project demonstrates a simple mock integration between Microsoft Teams and Taiga, where a Teams message (mocked via an API) creates a task in Taiga. The task is enriched using a local LLM (Llama3 via Ollama). It's designed as a take-home interview assessment and uses FastAPI for the API layer, with proper separation of concerns across routers, services, and API clients.

## Features

- Create Taiga tasks based on mock Teams messages
- Automatically generate descriptions using a local LLM
- Avoid duplicate task creation using fuzzy matching
- Mock creation of Microsoft Teams team and channels
- Link Teams teams to Taiga tasks
- Centralized logging to file
- Clean, testable, extensible architecture

## Project Structure
.
├── api/
│ ├── taiga.py # Exposes endpoints for Taiga task creation
│ └── teams.py # Exposes mocked Teams webhook and linking APIs
│
├── app/
│ ├── api_clients/
│ │ └── taiga_client.py # Raw HTTP logic for interacting with Taiga
│ ├── services/
│ │ ├── taiga_service.py # Business logic layer for task handling
│ │ ├── llm_service.py # Calls Ollama for description enrichment
│ │ └── teams_service.py # In-memory mock team creation
│ ├── logger/
│ │ └── logger.py # File logger setup using logging module
│ ├── utils/
│ │ └── utils.py # Utility functions, no external deps
│ └── config.py # Loads environment variables and constants
│
├── logs/ # Log file directory
├── .gitignore
├── README.md
└── main.py # FastAPI entry point

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

## API Usage
### 1. Trigger a mock Teams message to create a task
```bash
curl -X POST http://127.0.0.1:8000/teams/ \
     -H "Content-Type: application/json" \
     -d '{"text": "Setup deployment pipeline for staging"}'
```
This will:
- Check if a similar task already exists in Taiga
- If not, use LLM to enrich the title with a description
- Create a task in Taiga

### 2. Manually create a task (optional)
```bash
curl -X POST http://127.0.0.1:8000/taiga/create-task \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Optimize DB queries",
           "description": "Refactor slow queries in reports module"
         }'
```

### 3. Create a task and link it with a mocked team
```bash
curl -X POST http://127.0.0.1:8000/teams/create-task-with-team \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Integrate PayPal",
           "team_name": "Payments",
           "team_description": "Handles all payment gateway logic"
         }'
```

### 4. Retrieve linked team by task ID
```bash
curl http://127.0.0.1:8000/teams/team-by-task/12345
```

### Logs
Logs are saved in the logs/teams_taiga_integration.log file. Logging includes:
- Task creation events
- Duplicate detection
- LLM enrichment calls
- Errors from Taiga or Ollama

### API Testing with Insomnia
You can quickly test the integration using Insomnia REST client.

Steps:
- Open Insomnia.
- Go to Application Menu → Import/Export → Import Data → From Raw Text.
- Paste the following JSON export:
<details> <summary><code>Click to expand the Insomnia JSON export</code></summary>
{
  "_type": "export",
  "__export_format": 4,
  "__export_date": "2025-06-17T00:00:00.000Z",
  "__export_source": "insomnia.desktop.app:v2023.5.8",
  "resources": [
    {
      "_id": "wrk_teams_taiga_integration",
      "created": 1718592000000,
      "description": "Simulates Microsoft Teams message ingestion and Taiga task creation.",
      "modified": 1718592000000,
      "name": "Teams-Taiga-Integration",
      "_type": "workspace"
    },
    {
      "_id": "req_send_teams_message",
      "created": 1718592001000,
      "modified": 1718592001000,
      "parentId": "wrk_teams_taiga_integration",
      "name": "Send Teams Message",
      "method": "POST",
      "url": "http://localhost:8000/teams",
      "body": {
        "mimeType": "application/json",
        "text": "{\n  \"text\": \"We need to add OAuth2 login support to the platform\"\n}"
      },
      "_type": "request"
    },
    {
      "_id": "req_create_task_taiga",
      "created": 1718592002000,
      "modified": 1718592002000,
      "parentId": "wrk_teams_taiga_integration",
      "name": "Create Task in Taiga Manually",
      "method": "POST",
      "url": "http://localhost:8000/taiga/create-task",
      "body": {
        "mimeType": "application/json",
        "text": "{\n  \"title\": \"Add logging to backend\",\n  \"description\": \"Enhance the backend by adding structured logs.\"\n}"
      },
      "_type": "request"
    }
  ]
}
</details>

- Once imported, you will see:
    - Send Teams Message – Simulates a message from Teams to trigger task creation in Taiga.
    - Create Task in Taiga Manually – Direct task creation for manual testing.

### Notes
- This project is a mock and does not interact with real Teams APIs.
- All team/channel logic is in-memory and not persisted.
- No caching is added in this version.
- Unit tests are not included.

### Future Enhancements
- Add Redis or SQL to persist team-task mappings
- Use real Teams APIs with OAuth
- Add token refresh logic and error handling for Taiga
- Add job queues for async LLM or task creation
- Add unit and integration tests

This project is intended to show practical API design, async logic (where relevant), and clean code structure. Built for learning and demonstration purposes.
