# Maven Backend

Node.js API Gateway for the Maven AI Investment Copilot.

This service sits between the React frontend and the Python AI Service.
It receives requests from the browser, routes them to the correct internal
service, and returns standardised responses. It contains no investment logic.

---

## Folder Structure

```
backend/
│
├── src/
│   ├── config/
│   │   └── index.js              Central env config + startup validation
│   │
│   ├── constants/
│   │   ├── api.js                Service name, API version, status strings
│   │   ├── errorCodes.js         Machine-readable error code registry
│   │   └── httpStatus.js         Named HTTP status code constants
│   │
│   ├── controllers/
│   │   └── health.controller.js  HTTP boundary for /api/health
│   │
│   ├── middleware/
│   │   ├── cors.middleware.js          CORS policy (explicit origin)
│   │   ├── errorHandler.middleware.js  Centralised error handler (last resort)
│   │   └── requestLogger.middleware.js Per-request logging with timing
│   │
│   ├── routes/
│   │   ├── health.routes.js      Route definitions for /health group
│   │   └── index.js              Root API router — mounts all route groups
│   │
│   ├── services/
│   │   └── health.service.js     Business logic for health status
│   │
│   ├── utils/
│   │   ├── logger.js             Structured logger (info/warn/error/debug)
│   │   └── response.js           Standardised success/error response helpers
│   │
│   ├── app.js                    Express app factory (middleware + routes)
│   └── server.js                 Entry point (port binding + process signals)
│
├── .env.example                  Template for all required environment variables
├── Dockerfile                    Production container definition
└── package.json                  Dependencies and npm scripts
```

---

## How to Run

### Prerequisites

- Node.js >= 20.0.0
- npm >= 9.0.0

### Setup

```bash
# 1. Install dependencies
npm install

# 2. Create your environment file
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux

# 3. Start the development server (auto-restarts on file changes)
npm run dev

# 4. Start in production mode
npm start
```

### Expected Startup Output

```
══════════════════════════════════════════════════════
  ◆  Maven AI Investment Copilot
══════════════════════════════════════════════════════
  Service         maven-backend
  Version         1.0.0
  API             v1
  Environment     development
  Port            4000
  Health          http://localhost:4000/api/health
══════════════════════════════════════════════════════

[INFO ] 2026-06-27T...  Server is ready to accept connections.
```

---

## Environment Variables

All variables are documented in [`.env.example`](./.env.example).

| Variable | Required | Default | Description |
|---|---|---|---|
| `NODE_ENV` | No | `development` | Runtime environment (`development` \| `production` \| `test`) |
| `PORT` | No | `4000` | TCP port the server listens on |
| `CORS_ORIGIN` | Yes | `http://localhost:3000` | Exact origin of the React frontend |
| `AI_SERVICE_URL` | No | `http://localhost:8000` | Base URL of the Python AI service |
| `AI_SERVICE_TIMEOUT` | No | `30000` | Max ms to wait for a Python response |

> **Note:** The server will **not start** if any required variable is missing or
> invalid. It will print a clear error message and exit with code 1.

---

## API Response Contract

All endpoints return responses in one of these two shapes.
This contract is frozen — all future Maven endpoints must follow it.

### Success

```json
{
  "status": "success",
  "data": {
    "...": "payload specific to the endpoint"
  },
  "meta": {
    "...": "optional metadata: pagination, timestamps, counts"
  }
}
```

### Error

```json
{
  "status": "error",
  "error": {
    "code":    "MACHINE_READABLE_CODE",
    "message": "Human-readable explanation of what went wrong.",
    "details": {}
  }
}
```

**`details`** is only present in `development` mode (never in production).
It may contain a stack trace for debugging.

---

## Health Endpoint

### `GET /api/health`

Returns the current health status of this service.

**No authentication required.** This endpoint must always be reachable by
load balancers, Docker health checks, and monitoring tools.

**Response:**

```json
{
  "status": "success",
  "data": {
    "service":   "maven-backend",
    "version":   "1.0.0",
    "status":    "healthy",
    "uptime":    42.391,
    "timestamp": "2026-06-27T14:30:00.000Z"
  },
  "meta": {}
}
```

| Field | Type | Description |
|---|---|---|
| `service` | string | Canonical service identifier |
| `version` | string | Application version from `package.json` |
| `status` | string | `healthy` \| `degraded` \| `unhealthy` |
| `uptime` | number | Seconds since the process started |
| `timestamp` | string | ISO 8601 UTC timestamp of this response |

---

## Project Conventions

### Module Boundaries

| File Type | Responsibility | Must NOT |
|---|---|---|
| `routes/*.routes.js` | Map HTTP method + path to controller | Contain logic |
| `controllers/*.controller.js` | Receive HTTP, call service, return response | Contain business logic |
| `services/*.service.js` | Business logic, data transformation | Know about HTTP |
| `middleware/*.middleware.js` | Cross-cutting concerns (auth, CORS, logging) | Contain route logic |
| `utils/` | Shared pure helpers (logging, responses) | Have side effects |
| `constants/` | Immutable values | Be imported circularly |

### No Direct `process.env` Reads

The rest of the application never reads `process.env` directly.
All configuration is imported from `src/config/index.js`.

### No `console.log` in Application Code

All logging goes through `src/utils/logger.js`.
`console.log` is used only in the startup banner (an intentional exception).

### Response Envelope

Every endpoint uses `sendSuccess()` or `sendError()` from `src/utils/response.js`.
No endpoint constructs its own `res.status().json()` response shape.

### Error Codes

All error `code` values come from `src/constants/errorCodes.js`.
Raw strings like `'NOT_FOUND'` must never appear in application code.
