from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.pricing import Pricing
from app.models.product import Product
from app.monitoring.logger import logger

def create_pricing_lookup_tool(db: Session):

    @tool
    def get_customer_pricing(
        customer_code: str,
        sku: str,
    ) -> dict:
        """
        Retrieve the authoritative price for a product
        based on the customer's pricing tier.
        """
        logger.info(
            "Tool invoked: get_customer_pricing"
        )

        customer = (
            db.query(Customer)
            .filter(
                Customer.customer_code
                == customer_code
            )
            .first()
        )

        if not customer:
            raise ValueError(
                f"Customer not found: {customer_code}"
            )

        product = (
            db.query(Product)
            .filter(Product.sku == sku)
            .first()
        )

        if not product:
            raise ValueError(
                f"Product not found: {sku}"
            )

        pricing = (
            db.query(Pricing)
            .filter(
                Pricing.product_id == product.id,
                Pricing.pricing_tier
                == customer.pricing_tier,
            )
            .first()
        )

        if not pricing:
            raise ValueError(
                "Pricing not found"
            )

        return {
            "customer_code": customer.customer_code,
            "sku": product.sku,
            "pricing_tier": customer.pricing_tier,
            "unit_price": float(pricing.unit_price),
        }

    return get_customer_pricing