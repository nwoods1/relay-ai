from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.quote import QuoteRequest, QuoteResponse
from app.services.quote_service import create_quote


router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"]
)


@router.post(
    "/",
    response_model=QuoteResponse
)
def generate_quote(
    quote_request: QuoteRequest,
    db: Session = Depends(get_db),
):
    return create_quote(
        quote_request=quote_request,
        db=db,
    )