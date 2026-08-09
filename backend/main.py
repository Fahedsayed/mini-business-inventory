from fastapi import FastAPI

from config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "healthy"}
