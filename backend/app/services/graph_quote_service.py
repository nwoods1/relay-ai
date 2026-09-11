from sqlalchemy.orm import Session

from app.graph.workflow import quote_workflow
from app.schemas.quote import QuoteResponse


def create_quote_with_graph(
    message: str,
    db: Session,
) -> QuoteResponse:

    result = quote_workflow.invoke(
        {
            "message": message,
            "db": db,
        }
    )

    return result["quote"]