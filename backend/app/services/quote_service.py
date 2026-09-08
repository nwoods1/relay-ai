from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product
from app.models.pricing import Pricing
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse

from app.schemas.quote import (
    QuoteRequest,
    QuoteResponse,
    WarehouseAllocation,
)


def calculate_fulfillment_status(
    requested: int,
    available: int,
) -> str:
    if available >= requested:
        return "available"

    if available > 0:
        return "partial"

    return "unavailable"


def build_warehouse_allocations(
    inventory_rows,
    requested_quantity: int,
) -> list[WarehouseAllocation]:
    allocations = []
    remaining_quantity = requested_quantity

    for inventory, warehouse in inventory_rows:
        if remaining_quantity <= 0:
            break

        available_to_sell = max(
            inventory.quantity_available
            - inventory.quantity_reserved,
            0,
        )

        quantity_from_warehouse = min(
            available_to_sell,
            remaining_quantity,
        )

        if quantity_from_warehouse > 0:
            allocations.append(
                WarehouseAllocation(
                    warehouse_code=warehouse.code,
                    quantity=quantity_from_warehouse,
                )
            )

            remaining_quantity -= quantity_from_warehouse

    return allocations


def determine_approval_reasons(
    credit_status: str,
    subtotal: Decimal,
    fulfillment_status: str,
) -> list[str]:
    approval_reasons = []

    if credit_status != "approved":
        approval_reasons.append(
            "Customer credit status requires review"
        )

    if subtotal > Decimal("20000.00"):
        approval_reasons.append(
            "Quote exceeds $20,000 approval threshold"
        )

    if fulfillment_status == "partial":
        approval_reasons.append(
            "Requested quantity cannot be fully fulfilled"
        )

    if fulfillment_status == "unavailable":
        approval_reasons.append(
            "Product is currently unavailable"
        )

    return approval_reasons


def create_quote(
    quote_request: QuoteRequest,
    db: Session,
) -> QuoteResponse:

    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_code == quote_request.customer_code
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    product = (
        db.query(Product)
        .filter(
            Product.sku == quote_request.sku
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
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
            detail="Pricing not found",
        )

    inventory_rows = (
        db.query(Inventory, Warehouse)
        .join(
            Warehouse,
            Inventory.warehouse_id == Warehouse.id,
        )
        .filter(
            Inventory.product_id == product.id
        )
        .all()
    )

    total_available = sum(
        max(
            inventory.quantity_available
            - inventory.quantity_reserved,
            0,
        )
        for inventory, warehouse in inventory_rows
    )

    fulfillment_status = calculate_fulfillment_status(
        requested=quote_request.quantity,
        available=total_available,
    )

    allocations = build_warehouse_allocations(
        inventory_rows=inventory_rows,
        requested_quantity=quote_request.quantity,
    )

    unit_price = Decimal(pricing.unit_price)

    fulfillable_quantity = min(
        quote_request.quantity,
        total_available,
    )

    subtotal = unit_price * fulfillable_quantity

    approval_reasons = determine_approval_reasons(
        credit_status=customer.credit_status,
        subtotal=subtotal,
        fulfillment_status=fulfillment_status,
    )

    requires_approval = len(approval_reasons) > 0

    return QuoteResponse(
        customer_code=customer.customer_code,
        customer_name=customer.name,

        sku=product.sku,
        product_name=product.name,

        quantity_requested=quote_request.quantity,
        quantity_available=total_available,

        fulfillment_status=fulfillment_status,

        pricing_tier=customer.pricing_tier,
        unit_price=unit_price,
        subtotal=subtotal,

        credit_status=customer.credit_status,

        requires_approval=requires_approval,
        approval_reasons=approval_reasons,

        warehouse_allocations=allocations,
    )