from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings

app = FastAPI(title=settings.app_name)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class HealthResponse(BaseModel):
    status: str
    message: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", response_model=HealthResponse)
async def health(db: Session = Depends(get_db)):
    """Health check endpoint."""
    return {"status": "ok", "message": "healthy"}
