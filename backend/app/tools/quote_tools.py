from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.schemas.quote import QuoteRequest
from app.services.quote_service import create_quote
from app.monitoring.logger import logger


def create_quote_tool(db: Session):

    @tool
    def generate_quote(
        customer_code: str,
        sku: str,
        quantity: int,
    ) -> dict:
        """
        Generate a deterministic quote using authoritative
        customer, product, pricing, and inventory systems.
        """
        logger.info(
            "Tool invoked: create_quote_tool"
        )

        quote_request = QuoteRequest(
            customer_code=customer_code,
            sku=sku,
            quantity=quantity,
        )

        quote = create_quote(
            quote_request=quote_request,
            db=db,
        )

        return quote.model_dump(
            mode="json"
        )

    return generate_quote