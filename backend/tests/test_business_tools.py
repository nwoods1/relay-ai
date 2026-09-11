from app.core.database import SessionLocal
from app.tools.customer_tools import (
    create_customer_lookup_tool,
)
from app.tools.product_tools import (
    create_product_lookup_tool,
)
from app.tools.inventory_tools import (
    create_inventory_lookup_tool,
)
from app.tools.pricing_tools import (
    create_pricing_lookup_tool,
)
from app.tools.quote_tools import (
    create_quote_tool,
)


def test_customer_lookup_tool():
    db = SessionLocal()

    try:
        tool = create_customer_lookup_tool(
            db
        )

        result = tool.invoke(
            {
                "customer_name":
                    "Pacific Mountain Outfitters"
            }
        )

        assert (
            result["customer_code"]
            == "BP-20001"
        )

    finally:
        db.close()


def test_product_lookup_tool():
    db = SessionLocal()

    try:
        tool = create_product_lookup_tool(
            db
        )

        result = tool.invoke(
            {
                "product_name":
                    "Alpine Shell Jacket"
            }
        )

        assert (
            result["sku"]
            == "JACKET-BETA-AR-M"
        )

    finally:
        db.close()


def test_inventory_tool():
    db = SessionLocal()

    try:
        tool = create_inventory_lookup_tool(
            db
        )

        result = tool.invoke(
            {
                "sku": "JACKET-BETA-AR-M"
            }
        )

        assert result["total_available"] == 89

    finally:
        db.close()


def test_pricing_tool():
    db = SessionLocal()

    try:
        tool = create_pricing_lookup_tool(
            db
        )

        result = tool.invoke(
            {
                "customer_code": "BP-20001",
                "sku": "JACKET-BETA-AR-M",
            }
        )

        assert (
            result["pricing_tier"] == "B"
        )

        assert (
            result["unit_price"] == 714.99
        )

    finally:
        db.close()

def test_quote_tool():
    db = SessionLocal()

    try:
        tool = create_quote_tool(
            db
        )

        result = tool.invoke(
            {
                "customer_code": "BP-20001",
                "sku": "JACKET-BETA-AR-M",
                "quantity": 30,
            }
        )

        assert (
            result["customer_code"]
            == "BP-20001"
        )

        assert (
            result["quantity_requested"]
            == 30
        )

    finally:
        db.close()