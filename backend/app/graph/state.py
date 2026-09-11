from typing import TypedDict

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product
from app.schemas.ai import ParsedQuoteRequest
from app.schemas.quote import QuoteResponse


class QuoteWorkflowState(TypedDict, total=False):
    message: str

    db: Session

    current_node: str | None

    parsed_request: ParsedQuoteRequest

    customer: Customer
    product: Product

    quote: QuoteResponse

    requires_approval: bool
    approval_reasons: list[str]
    workflow_status: str | None

    error: str | None