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

### Database configuration

The backend uses SQLAlchemy for database access.

- `DATABASE_URL` configures the SQLAlchemy connection URL.
- Default value is `sqlite:///:memory:` for local development.
- The SQLAlchemy engine is created in `backend/main.py`.
- `SessionLocal` is the session factory.
- `get_db` is a FastAPI dependency that yields a session and closes it after the request.
