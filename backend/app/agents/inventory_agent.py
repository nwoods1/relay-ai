from sqlalchemy.orm import Session

from app.tools.inventory_tools import (
    create_inventory_lookup_tool,
)
from app.tools.product_tools import (
    create_product_lookup_tool,
)


def run_inventory_agent(
    db: Session,
    product_name: str,
) -> dict:

    product_tool = (
        create_product_lookup_tool(db)
    )

    product_data = product_tool.invoke(
        {
            "product_name":
                product_name
        }
    )

    inventory_tool = (
        create_inventory_lookup_tool(db)
    )

    inventory_data = (
        inventory_tool.invoke(
            {
                "sku":
                    product_data["sku"]
            }
        )
    )

    return {
        "product": product_data,
        "inventory": inventory_data,
    }