from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    message: str


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
