from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_permission,
)
from app.core.database import get_db
from app.models.user import User

from app.schemas.dashboard import (
    DashboardActivityListResponse,
    DashboardApprovalListResponse,
    DashboardInventoryListResponse,
    DashboardOverviewResponse,
    DashboardQuoteListResponse,
    DashboardWarehouseListResponse,
)

from app.services.dashboard_service import (
    get_dashboard_activity,
    get_dashboard_approvals,
    get_dashboard_inventory,
    get_dashboard_overview,
    get_dashboard_quotes,
    get_dashboard_warehouses,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
def dashboard_overview(
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    return get_dashboard_overview(
        db=db
    )


@router.get(
    "/quotes",
    response_model=(
        DashboardQuoteListResponse
    ),
)
def dashboard_quotes(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    status: str | None = Query(
        default=None
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    return get_dashboard_quotes(
        db=db,
        limit=limit,
        status=status,
    )


@router.get(
    "/inventory",
    response_model=(
        DashboardInventoryListResponse
    ),
)
def dashboard_inventory(
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    return get_dashboard_inventory(
        db=db,
        search=search,
    )


@router.get(
    "/warehouses",
    response_model=(
        DashboardWarehouseListResponse
    ),
)
def dashboard_warehouses(
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    return get_dashboard_warehouses(
        db=db
    )


@router.get(
    "/approvals",
    response_model=(
        DashboardApprovalListResponse
    ),
)
def dashboard_approvals(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    status: str | None = Query(
        default=None
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    return get_dashboard_approvals(
        db=db,
        limit=limit,
        status=status,
    )


@router.get(
    "/activity",
    response_model=(
        DashboardActivityListResponse
    ),
)
def dashboard_activity(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    status: str | None = Query(
        default=None
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    return get_dashboard_activity(
        db=db,
        limit=limit,
        status=status,
    )