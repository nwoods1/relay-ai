from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.services.entity_resolution_service import resolve_product


def create_product_lookup_tool(db: Session):

    @tool
    def lookup_product(product_name: str) -> dict:
        """
        Look up a product by name and return authoritative
        product catalog information.
        """

        product = resolve_product(
            product_name=product_name,
            db=db,
        )

        return {
            "sku": product.sku,
            "product_name": product.name,
            "category": product.category,
            "unit_size": product.unit_size,
            "base_price": float(product.base_price),
        }

    return lookup_product