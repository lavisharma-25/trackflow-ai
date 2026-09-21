# TrackFlow backend

FastAPI backend for TrackFlow AI. It owns validation, persistence, audit history,
conversation history, and the Gemini tool layer.

```powershell
uv sync
uv run uvicorn main:app --reload
```

Run tests with `uv run pytest`. Interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

See the repository root README for the data model, configuration, and full-stack setup.
