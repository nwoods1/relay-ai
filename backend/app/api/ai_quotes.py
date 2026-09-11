from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ai import NaturalLanguageQuoteRequest
from app.schemas.quote import QuoteResponse
from app.services.graph_quote_service import (
    create_quote_with_graph,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

@router.post(
    "/quote",
    response_model=QuoteResponse,
)
def generate_quote_from_text(
    request: NaturalLanguageQuoteRequest,
    db: Session = Depends(get_db),
):
    try:
        return create_quote_with_graph(
            message=request.message,
            db=db,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )