from app.schemas.ai import ParsedQuoteRequest
from sqlalchemy.orm import Session

from app.llm.bedrock import parse_quote_request
from app.schemas.quote import QuoteRequest, QuoteResponse
from app.services.entity_resolution_service import (
    resolve_customer,
    resolve_product,
)
from app.services.quote_service import create_quote


def validate_parsed_quote_request(
    parsed_request: ParsedQuoteRequest,
):
    missing_fields = []

    if not parsed_request.customer_name:
        missing_fields.append("customer")

    if not parsed_request.product_name:
        missing_fields.append("product")

    if not parsed_request.quantity:
        missing_fields.append("quantity")

    if missing_fields:
        raise ValueError(
            "Missing required information: "
            + ", ".join(missing_fields)
        )

def create_quote_from_text(
    message: str,
    db: Session,
) -> QuoteResponse:

    parsed_request = parse_quote_request(
        message=message
    )

    validate_parsed_quote_request(
        parsed_request
    )

    customer = resolve_customer(
        customer_name=parsed_request.customer_name,
        db=db,
    )

    product = resolve_product(
        product_name=parsed_request.product_name,
        db=db,
    )

    quote_request = QuoteRequest(
        customer_code=customer.customer_code,
        sku=product.sku,
        quantity=parsed_request.quantity,
    )

    return create_quote(
        quote_request=quote_request,
        db=db,
    )

