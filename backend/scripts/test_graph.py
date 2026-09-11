from app.core.database import SessionLocal
from app.graph.workflow import quote_workflow


def test_graph():
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
            result["customer"].name,
        )

        print(
            "Product:",
            result["product"].name,
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
    test_graph()