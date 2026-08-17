from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import Product
from repository import create_product
from schemas import HealthResponse, ProductCreate, ProductResponse

app = FastAPI(title=settings.app_name)


@app.get("/health", response_model=HealthResponse)
async def health(db: Session = Depends(get_db)):
    """Health check endpoint."""
    return {"status": "ok", "message": "healthy"}


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
):
    """Create a new product."""
    product = Product(name=product_in.name, sku=product_in.sku)
    return create_product(db, product)
