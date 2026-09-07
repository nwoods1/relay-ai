from decimal import Decimal

from pydantic import BaseModel


class PricingResponse(BaseModel):
    customer_code: str
    customer_name: str
    sku: str
    product_name: str
    pricing_tier: str
    unit_price: Decimal