from app.core.database import SessionLocal
from app.graph.workflow import quote_workflow


def run_graph():
    db = SessionLocal()

    try:
        result = quote_workflow.invoke(
            {
                "message": (
                    "Pacific Mountain Outfitters wants "
                    "1 Merino Wool Toque."
                ),
                "db": db,
            }
        )

        print(
            "Workflow status:",
            result["workflow_status"],
        )

        print("\nGRAPH RESULT")
        print("------------")

        print(
            "Parsed:",
            result["parsed_request"],
        )

        print(
            "Customer:",
            result["customer_data"]["customer_name"],
        )

        print(
            "Customer code:",
            result["customer_data"]["customer_code"],
        )

        print(
            "Product:",
            result["product_data"]["product_name"],
        )

        print(
            "SKU:",
            result["product_data"]["sku"],
        )

        print(
            "Inventory:",
            result["inventory_data"],
        )

        print(
            "Pricing:",
            result["pricing_data"],
        )

        print(
            "Quote:",
            result["quote"],
        )

        print(
            "Requires approval:",
            result["requires_approval"],
        )

        print(
            "Approval reasons:",
            result["approval_reasons"],
        )

    finally:
        db.close()


if __name__ == "__main__":
    run_graph()