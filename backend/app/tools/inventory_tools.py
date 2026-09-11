from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.monitoring.logger import logger

def create_inventory_lookup_tool(db: Session):

    @tool
    def check_inventory(sku: str) -> dict:
        """
        Check sellable inventory for a product across all
        warehouses using the authoritative inventory database.
        """
        logger.info(
            "Tool invoked: check_inventory"
        )

        product = (
            db.query(Product)
            .filter(Product.sku == sku)
            .first()
        )

        if not product:
            raise ValueError(
                f"Product not found for SKU: {sku}"
            )

        rows = (
            db.query(Inventory, Warehouse)
            .join(
                Warehouse,
                Inventory.warehouse_id
                == Warehouse.id,
            )
            .filter(
                Inventory.product_id
                == product.id
            )
            .all()
        )

        warehouses = []
        total_available = 0

        for inventory, warehouse in rows:
            sellable = max(
                inventory.quantity_available
                - inventory.quantity_reserved,
                0,
            )

            total_available += sellable

            warehouses.append(
                {
                    "warehouse_code": warehouse.code,
                    "warehouse_name": warehouse.name,
                    "sellable_quantity": sellable,
                }
            )

        return {
            "sku": product.sku,
            "product_name": product.name,
            "total_available": total_available,
            "warehouses": warehouses,
        }

    return check_inventory