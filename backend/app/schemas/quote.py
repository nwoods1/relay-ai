from decimal import Decimal

from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    customer_code: str
    sku: str
    quantity: int = Field(gt=0)


class WarehouseAllocation(BaseModel):
    warehouse_code: str
    quantity: int


class QuoteResponse(BaseModel):
    customer_code: str
    customer_name: str

    sku: str
    product_name: str

    quantity_requested: int
    quantity_available: int

    fulfillment_status: str

    pricing_tier: str
    unit_price: Decimal
    subtotal: Decimal


    credit_status: str
    requires_approval: bool
    approval_reasons: list[str]
    warehouse_allocations: list[WarehouseAllocation]