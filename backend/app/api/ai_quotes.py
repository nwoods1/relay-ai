from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai import (
    NaturalLanguageQuoteRequest,
)
from app.schemas.workflow import (
    QuoteWorkflowResponse,
)
from app.services.graph_quote_service import (
    create_quote_with_graph,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/quote",
    response_model=QuoteWorkflowResponse,
)
def generate_quote_from_text(
    request: NaturalLanguageQuoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("quote:create")
    ),
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=8,
        max_length=255,
    ),
):
    try:
        return create_quote_with_graph(
            message=request.message,
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role,
            idempotency_key=idempotency_key,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc