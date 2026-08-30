from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    message: str


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)

    @field_validator("name", "sku")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or whitespace only")
        return stripped


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)

    @field_validator("name", "sku")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or whitespace only")
        return stripped


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
