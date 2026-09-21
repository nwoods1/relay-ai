from typing import TypedDict

from app.models.customer import Customer
from app.models.product import Product
from app.schemas.ai import ParsedQuoteRequest
from app.schemas.quote import QuoteResponse


class QuoteWorkflowState(TypedDict, total=False):
    message: str

    user_id: int | None
    username: str | None
    user_role: str | None

    current_node: str | None

    parsed_request: ParsedQuoteRequest

    customer_data: dict | None
    product_data: dict | None
    inventory_data: dict | None
    pricing_data: dict | None

    quote: QuoteResponse

    requires_approval: bool
    approval_reasons: list[str]

    workflow_status: str | None

    approval_decision: str | None
    approved_by_user_id: int | None
    approved_by_username: str | None
    approval_comment: str | None

    error_type: str | None
    error_message: str | None
    failed_node: str | None
    retry_count: int | None

    error: str | None
    workflow_run_id: int | None