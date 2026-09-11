from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.services.entity_resolution_service import resolve_customer
from app.monitoring.logger import logger

def create_customer_lookup_tool(db: Session):

    @tool
    def lookup_customer(customer_name: str) -> dict:
        """
        Look up a customer by name and return authoritative
        customer information from the CRM database.
        """
        logger.info(
            "Tool invoked: lookup_customer"
        )

        customer = resolve_customer(
            customer_name=customer_name,
            db=db,
        )

        return {
            "customer_code": customer.customer_code,
            "customer_name": customer.name,
            "region": customer.region,
            "credit_status": customer.credit_status,
            "pricing_tier": customer.pricing_tier,
        }

    return lookup_customer