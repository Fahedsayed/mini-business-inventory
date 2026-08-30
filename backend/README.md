# Backend

Minimal FastAPI backend for the Mini Business Inventory System.

## Run locally

From the `backend/` directory:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

## API Endpoints

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Create product

```bash
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "sku": "TEST-001"}'
```

### Retrieve product

```bash
curl http://127.0.0.1:8000/products/1
```

### List products

```bash
curl "http://127.0.0.1:8000/products?limit=20&offset=0"
```

`limit` defaults to `20` and may be at most `100`. `offset` defaults to `0`.

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

### Architecture & Layer Responsibilities

The backend follows a layered architecture with clean separation of concerns:

```text
HTTP / API (main.py)
       ↓
Repository (repository.py)
       ↓
SQLAlchemy Session (database.py)
       ↓
Database (SQLite)
```

- **API Routes (`main.py`)**: Thin FastAPI endpoints handling HTTP routing, dependency injection (`get_db`), request validation via Pydantic schemas, HTTP exception mapping, and response serialization.
- **Repository (`repository.py`)**: Data access layer encapsulating all SQLAlchemy queries, model entity instantiation, and database transactions.
- **Schemas (`schemas.py`)**: Pydantic v2 models for API input validation and output serialization (`ProductCreate`, `ProductUpdate`, `ProductResponse`).
- **Models (`models.py`)**: SQLAlchemy declarative ORM models representing database tables and constraints (`Product`).
- **Database (`database.py`)**: Database engine configuration, session management, and `get_db` generator dependency.

### Data access

The backend isolates database operations using repository functions in `backend/repository.py`:

- `create_product(db, name, sku)`: Instantiates, persists, and refreshes a `Product` entity.
- `get_product_by_id(db, product_id)`: Retrieves a `Product` by its primary key ID.
- `list_products(db, limit, offset)`: Retrieves a page of `Product` entities ordered deterministically by ID ascending.
- `update_product(db, product_id, name, sku)`: Updates and persists changes to an existing `Product`.
- `delete_product(db, product_id)`: Deletes a `Product` entity from the database.
