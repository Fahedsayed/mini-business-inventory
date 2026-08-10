from fastapi import FastAPI
from pydantic import BaseModel

from config import settings

app = FastAPI(title=settings.app_name)


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "healthy"}
