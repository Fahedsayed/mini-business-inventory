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
- The SQLAlchemy engine, declarative `Base`, and `SessionLocal` are defined in `backend/database.py`.
- `get_db` is a FastAPI dependency that yields a session and closes it after the request.

### Database migrations

The backend uses **Alembic** to manage database schema migrations.

From the `backend/` directory:

- Apply all migrations:
  ```bash
  alembic upgrade head
  ```
- Revert the last applied migration:
  ```bash
  alembic downgrade -1
  ```
- View current migration revision:
  ```bash
  alembic current
  ```
- Generate a new migration based on SQLAlchemy model changes:
  ```bash
  alembic revision --autogenerate -m "describe change"
  ```
