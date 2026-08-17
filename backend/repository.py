from typing import Optional

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
