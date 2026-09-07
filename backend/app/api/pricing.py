from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.pricing import Pricing
from app.schemas.pricing import PricingResponse


router = APIRouter(
    prefix="/pricing",
    tags=["Pricing"]
)


@router.get(
    "/{customer_code}/{sku}",
    response_model=PricingResponse
)
def get_customer_pricing(
    customer_code: str,
    sku: str,
    db: Session = Depends(get_db)
):
    customer = (
        db.query(Customer)
        .filter(Customer.customer_code == customer_code)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    product = (
        db.query(Product)
        .filter(Product.sku == sku)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    pricing = (
        db.query(Pricing)
        .filter(
            Pricing.product_id == product.id,
            Pricing.pricing_tier == customer.pricing_tier,
        )
        .first()
    )

    if not pricing:
        raise HTTPException(
            status_code=404,
            detail="Pricing not found for this customer and product"
        )

    return PricingResponse(
        customer_code=customer.customer_code,
        customer_name=customer.name,
        sku=product.sku,
        product_name=product.name,
        pricing_tier=customer.pricing_tier,
        unit_price=pricing.unit_price,
    )