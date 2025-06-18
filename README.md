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

## Workflow Summary
- Message is received from Teams.
- All current stories and sub-tasks are fetched.
- LLM checks for:
  - Duplicate user story
  - Sub-task under an existing story
  - Semantic similarity to any story
- If not a duplicate:
  - Sub-task is created under matched story or
  - A new story is created
- Priority is auto-fetched per project and assigned accordingly.

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
### 1. POST /api/taiga/teams-webhook
Processes a Microsoft Teams webhook message.
```bash
curl -X POST http://127.0.0.1:8000/teams/webhook \
     -H "Content-Type: application/json" \
     -d '{"text": "Investigate why the staging environment is not syncing with production."}'
```
This will:
- Check if a similar task already exists in Taiga
- If not, use LLM to enrich the title with a description
- Create a task in Taiga

### 2. POST /api/teams/webhook
Alternative, simpler endpoint for handling Teams messages.
```bash
curl -X POST http://127.0.0.1:8000/taiga/webhook \
     -H "Content-Type: application/json" \
     -d '{"title": "Check DNS between pre-prod and prod"}'
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
  "__export_format": 5,
  "__export_date": "2025-06-17T00:00:00.000Z",
  "__export_source": "insomnia.desktop",
  "resources": [
    {
      "_id": "wrk_71f6a7877ea34237898effcd7ee879d4",
      "created": 1750200563795,
      "description": "",
      "modified": 1750200563795,
      "name": "Teams Taiga LLM Integration",
      "type": "workspace",
      "_type": "workspace"
    },
    {
      "_id": "req_804f47a50ee0412788fd413fe0e49211",
      "parentId": "wrk_71f6a7877ea34237898effcd7ee879d4",
      "modified": 1750231596583,
      "created": 1750229033989,
      "url": "http://localhost:8000/teams/webhook",
      "name": "Create a Story from Teams",
      "method": "POST",
      "body": {
        "mimeType": "application/json",
        "text": "{\n     \"text\": \"Investigate why the staging environment is not syncing with production.\"\n}"
      },
      "headers": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ],
      "parameters": [],
      "authentication": {},
      "metaSortKey": -1750229033989,
      "isPrivate": false,
      "_type": "request"
    },
    {
      "_id": "req_36bec15465c24a6a85e9d2755621f237",
      "parentId": "wrk_71f6a7877ea34237898effcd7ee879d4",
      "modified": 1750237758994,
      "created": 1750229662619,
      "url": "http://localhost:8000/teams/webhook",
      "name": "Create a sub task",
      "method": "POST",
      "body": {
        "mimeType": "application/json",
        "text": "{\"text\": \"Review DNS between pre-prod and prod\"}"
      },
      "headers": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ],
      "parameters": [],
      "authentication": {},
      "metaSortKey": -1750229662619,
      "isPrivate": false,
      "_type": "request"
    },
    {
      "_id": "req_cf8ae085f9694ccb9e78e8e658305412",
      "parentId": "wrk_71f6a7877ea34237898effcd7ee879d4",
      "modified": 1750237851625,
      "created": 1750230780936,
      "url": "http://localhost:8000/teams/webhook",
      "name": "Create sub-task for relevant story",
      "method": "POST",
      "body": {
        "mimeType": "application/json",
        "text": "{\"text\": \"Check if the sync script runs via cron in staging\"}"
      },
      "headers": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ],
      "parameters": [],
      "authentication": {},
      "metaSortKey": -1750229348304,
      "isPrivate": false,
      "_type": "request"
    },
    {
      "_id": "jar_b74a24bd8d6ef7bc8f2992b50f4c981b6c43d223",
      "parentId": "wrk_71f6a7877ea34237898effcd7ee879d4",
      "modified": 1750200563801,
      "created": 1750200563801,
      "name": "Default Jar",
      "cookies": [],
      "_type": "cookie_jar"
    },
    {
      "_id": "env_b74a24bd8d6ef7bc8f2992b50f4c981b6c43d223",
      "parentId": "wrk_71f6a7877ea34237898effcd7ee879d4",
      "modified": 1750200563799,
      "created": 1750200563799,
      "name": "Base Environment",
      "data": {},
      "dataPropertyOrder": null,
      "color": null,
      "isPrivate": false,
      "metaSortKey": 1750200563799,
      "_type": "environment"
    },
    {
      "_id": "env_9a7a673646d7471e8cac8191cfa3fe0b",
      "parentId": "env_b74a24bd8d6ef7bc8f2992b50f4c981b6c43d223",
      "modified": 1750200579280,
      "created": 1750200579280,
      "name": "Base Environment",
      "data": {
        "base_url": "http://localhost:8000"
      },
      "dataPropertyOrder": {
        "&": [
          "base_url"
        ]
      },
      "color": null,
      "isPrivate": false,
      "metaSortKey": 1750200579280,
      "_type": "environment"
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
- Priorities are fetched using:
  ```bash
  GET /api/v1/priorities?project=<project_id>
  ```
- Description content is enriched using an LLM. 
- Handles empty or irrelevant input gracefully.
- Duplicates are avoided using semantic similarity logic.

### Future Enhancements
- Add Redis or SQL to persist team-task mappings
- Use real Teams APIs with OAuth
- Add token refresh logic and error handling for Taiga
- Add job queues for async LLM or task creation
- Add unit and integration tests

This project is intended to show practical API design, async logic (where relevant), and clean code structure. Built for learning and demonstration purposes.
