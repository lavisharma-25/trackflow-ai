# TrackFlow AI

TrackFlow AI is an AI-first universal tracker and personal second brain. It lets you
create flexible collections for expenses, habits, books, job applications, notes, or
anything else, then capture and retrieve information manually or through Gemini.

## Repository structure

```text
trackflow-ai/
├── backend/                 FastAPI, SQLAlchemy, SQLite, Gemini, tests
│   ├── main.py
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
├── frontend/                React, TypeScript, Vite
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

The applications are independent. The frontend communicates with the backend over its
REST API. The backend remains usable on its own through `/docs`.

## Features

### Frontend

- Responsive desktop and mobile workspace
- Collection navigation and creation
- Dynamic field builder with nine property types
- Item creation using each collection's schema
- Search across titles, notes, and properties
- Table and card views
- Confirmed archive actions
- Slide-out AI assistant with persistent conversation context
- Empty, loading, error, and disconnected-backend states

### Backend

- Collection and item CRUD
- Typed dynamic property validation
- SQLite persistence through SQLAlchemy
- Archive and restore instead of permanent deletion
- Activity/audit events
- Persistent assistant conversations
- One Gemini tool-using assistant
- Lazy AI initialization—the REST API works without Gemini credentials
- CORS configured for the local Vite application

## Run locally

### 1. Start the backend

```powershell
cd backend
uv sync
uv run uvicorn main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

- API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### 2. Start the frontend

Open another terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`.

## Configuration

Backend configuration belongs in `backend/.env`:

```env
SERVICE_ACCOUNT_PATH=G:/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id
LOCATION=global
GEMINI_MODEL_FLASH=gemini-2.5-flash
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

The backend also discovers the first JSON credential file in
`backend/model_credentials/`. Credentials, logs, and database storage are ignored by
Git.

Frontend configuration is optional. Copy `frontend/.env.example` to `.env` to change
the backend address:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## How the system works

```text
React UI
   |
   +-- direct action --> FastAPI route --> domain service --> SQLite
   |
   +-- natural language --> /assistant --> Gemini --> safe tools --+
                                                                  |
                                   conversation history <---------+
```

A **collection** defines reusable fields. An **item** contains a title, notes, and
properties matching those fields. For example, an Expenses collection can define
`amount`, `category`, and `spent_on`; every expense item is validated against that
definition.

Gemini only interprets requests and selects safe tools. Python services perform all
validation and database writes. The assistant has no deletion tool.

## Development checks

Backend:

```powershell
cd backend
uv run pytest
```

Frontend:

```powershell
cd frontend
npm.cmd run build
```

The current suite contains five backend tests covering validation, search, schema
safety, audit events, archive confirmation, and browser CORS.

## Storage

The active SQLite database is `backend/src/storage/trackflow.db`. It is the application's
single source of truth and is ignored by Git.

## Current scope

This is a local single-user application. Before exposing it publicly, add
authentication, workspace ownership, authorization, production database migrations,
and rate limiting. Saved views, backlinks, attachments, reminders, and hybrid vector
search are appropriate later milestones.
