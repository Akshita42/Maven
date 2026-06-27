# maven-ai-service (Python)

Stateless intelligence and agent layer for the Maven AI Investment Copilot.

---

## Project Purpose
The `maven-ai-service` is the intelligence center of the Maven architecture. It exists to run structured financial reasoning, analyze market data, and generate recommendations. It owns the core AI pipelines (such as the Six Pillars, Scenario Evaluator, and Investment Committee Critique) and outputs a structured `DecisionPackage` back to the Node.js orchestrator.

---

## Folder Structure

```
ai-service/
│
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   └── health.py        # Health check endpoint controller
│   │   └── router.py            # Central router mounting route groups
│   │
│   ├── config/
│   │   └── settings.py          # Environment settings loader and startup validation
│   │
│   ├── constants/
│   │   ├── api.py               # Metadata, service identification, response envelopes
│   │   └── error_codes.py       # Stable error codes for client routing
│   │
│   ├── core/
│   │   └── __init__.py          # Shared infrastructure placeholders
│   │
│   ├── services/
│   │   └── health_service.py    # Business logic tracking startup time & calculating uptime
│   │
│   ├── utils/
│   │   ├── logger.py            # Colorized console logger with level-filtering
│   │   └── response.py          # Success and error HTTP response wrappers
│   │
│   └── main.py                  # Entrypoint configuring middlewares, exceptions, and routers
│
├── requirements.txt             # Third-party packages required
├── .env.example                 # Configuration template
├── Dockerfile                   # Service containerization manifest
└── README.md                    # Documentation
```

---

## How to Run

### Prerequisites
- Python >= 3.11
- Virtual environment tool (`venv` or `virtualenv`)

### Setup and Start

```bash
# 1. Create Python virtual environment
python -m venv .venv

# 2. Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create local environment file
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux

# 5. Start the development server (auto-reloads on file edits)
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Expected Startup Output
```
======================================================
  *  maven-ai-service
======================================================
  Service         maven-ai-service
  Version         1.0.0
  Environment     development
  Host            127.0.0.1
  Port            8000
  Health          http://127.0.0.1:8000/api/v1/health
======================================================

[INFO   ] 2026-06-27T...Z  AI Service is ready to accept queries.
```

---

## Environment Variables

All variables are configured via `.env`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENV` | No | `development` | Runtime environment (`development` \| `production` \| `test`) |
| `HOST` | No | `127.0.0.1` | Network interface to bind to |
| `PORT` | No | `8000` | Port to expose the FastAPI service on |

If an invalid `PORT` (e.g. out of range 1–65535) or unsupported `ENV` value is configured, the application will **fail-fast** and print error diagnostics before exiting.

---

## API Response Contract

Enforces consistency with the Node.js gateway.

### Success
```json
{
  "status": "success",
  "data": {
    "key": "value"
  },
  "meta": {}
}
```

### Error
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-friendly warning message.",
    "details": {}
  }
}
```

*Note: `details` containing stack traces is omitted in production.*

---

## Health Endpoint

### `GET /api/v1/health`

Returns service metadata and uptime in seconds.

**Response:**
```json
{
  "status": "success",
  "data": {
    "service": "maven-ai-service",
    "version": "1.0.0",
    "status": "healthy",
    "uptime": 1.458,
    "timestamp": "2026-06-27T14:30:00.000Z"
  },
  "meta": {}
}
```

---

## Project Conventions

- **Thin Route Handlers**: Route files located in `src/api/routes` must only define URL endpoints, route decorators, and dependency injections. They must forward execution to the service layer.
- **Pure Logic Services**: Code inside `src/services` handles data transformation and AI flows. It must remain stateless and have no knowledge of HTTP queries or parameters.
- **Fail Fast Configuration**: The configuration in `src/config/settings.py` validates values immediately. If a validation error is encountered, the service stops immediately.
- **No raw print() statements**: Developers must use the `logger` from `src/utils/logger.py` to print records to standard output, with the sole exception of the startup configuration status banner.
