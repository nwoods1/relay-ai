from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    unit_size: str
    base_price: Decimal

    model_config = ConfigDict(from_attributes=True)