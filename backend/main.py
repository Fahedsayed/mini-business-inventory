from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import Product
from repository import create_product, delete_product, get_product_by_id, list_products, update_product
from schemas import HealthResponse, ProductCreate, ProductResponse, ProductUpdate

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


@app.get(
    "/products",
    response_model=list[ProductResponse],
)
def list_all_products(
    db: Session = Depends(get_db),
):
    """Retrieve all products."""
    return list_products(db)


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a product by its ID."""
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def update_existing_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing product by its ID."""
    product = update_product(db, product_id, name=product_in.name, sku=product_in.sku)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Delete a product by its ID."""
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
