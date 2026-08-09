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
