from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Product


def create_product(db: Session, product: Product) -> Product:
    """Create and persist a new Product in the database.

    Args:
        db: Active SQLAlchemy database session.
        product: Product model instance to persist.

    Returns:
        The persisted Product instance with refreshed attributes.
    """
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """Retrieve a Product by its primary key ID.

    Args:
        db: Active SQLAlchemy database session.
        product_id: Integer primary key of the product.

    Returns:
        The Product instance if found, or None if not found.
    """
    return db.get(Product, product_id)


def list_products(db: Session) -> list[Product]:
    """Retrieve all Products ordered deterministically by ID ascending.

    Args:
        db: Active SQLAlchemy database session.

    Returns:
        List of Product instances.
    """
    stmt = select(Product).order_by(Product.id.asc())
    return list(db.scalars(stmt).all())


def update_product(db: Session, product_id: int, name: str, sku: str) -> Optional[Product]:
    """Update an existing Product's fields and persist the changes.

    Args:
        db: Active SQLAlchemy database session.
        product_id: Integer primary key of the product to update.
        name: New name value.
        sku: New SKU value.

    Returns:
        The updated Product instance, or None if no Product with that ID exists.
    """
    product = db.get(Product, product_id)
    if product is None:
        return None
    product.name = name
    product.sku = sku
    db.commit()
    db.refresh(product)
    return product
