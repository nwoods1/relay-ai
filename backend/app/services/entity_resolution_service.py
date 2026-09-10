from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product


def resolve_customer(
    customer_name: str,
    db: Session,
) -> Customer:

    customer = (
        db.query(Customer)
        .filter(
            Customer.name.ilike(
                f"%{customer_name}%"
            )
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer not found: {customer_name}"
        )

    return customer


def resolve_product(
    product_name: str,
    db: Session,
) -> Product:

    products = (
        db.query(Product)
        .filter(
            Product.name.ilike(
                f"%{product_name}%"
            )
        )
        .all()
    )

    if len(products) == 0 and product_name.lower().endswith("s"):
        singular_name = product_name[:-1]

        products = (
            db.query(Product)
            .filter(
                Product.name.ilike(
                    f"%{singular_name}%"
                )
            )
            .all()
        )

    if len(products) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Product not found: {product_name}"
        )

    if len(products) > 1:
        raise HTTPException(
            status_code=409,
            detail="Multiple products matched the request"
        )

    return products[0]