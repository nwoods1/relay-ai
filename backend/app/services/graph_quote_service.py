from sqlalchemy.orm import Session

from app.graph.workflow import quote_workflow
from app.schemas.quote import QuoteResponse


def create_quote_with_graph(
    message: str,
    db: Session,
    user_id: int,
    username: str,
    user_role: str,
) -> QuoteResponse:

    result = quote_workflow.invoke(
        {
            "message": message,
            "db": db,
            "user_id": user_id,
            "username": username,
            "user_role": user_role,
        }
    )

    return result["quote"]