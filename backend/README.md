# Backend

Minimal FastAPI backend for the Mini Business Inventory System.

## Run locally

From the `backend/` directory:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

## Health check

```bash
curl http://127.0.0.1:8000/health
```

## Configuration

The backend loads settings from environment variables and supports a `.env` file for development.

Copy `.env.example` to `.env` and adjust values as needed.
