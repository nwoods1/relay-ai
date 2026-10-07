from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class DashboardOverviewResponse(BaseModel):
    total_products: int
    total_customers: int
    total_warehouses: int

    total_physical_inventory: int
    total_reserved_inventory: int
    total_sellable_inventory: int

    total_workflows: int
    active_workflows: int
    completed_workflows: int
    failed_workflows: int

    pending_approvals: int


class DashboardQuoteItem(BaseModel):
    thread_id: str
    operation: str

    user_id: int
    username: str
    user_role: str

    status: str
    current_node: str | None = None

    requires_approval: bool

    error_type: str | None = None
    error_message: str | None = None

    retry_count: int

    input_tokens: int
    output_tokens: int
    total_tokens: int

    llm_latency_ms: float | None = None
    duration_ms: float | None = None

    started_at: datetime
    completed_at: datetime | None = None


class DashboardQuoteListResponse(BaseModel):
    items: list[DashboardQuoteItem] = Field(
        default_factory=list
    )

    total: int


class DashboardInventoryItem(BaseModel):
    product_id: int

    sku: str
    product_name: str
    category: str
    unit_size: str

    physical_quantity: int
    reserved_quantity: int
    sellable_quantity: int


class DashboardInventoryListResponse(BaseModel):
    items: list[DashboardInventoryItem] = Field(
        default_factory=list
    )

    total: int


class DashboardWarehouseInventoryItem(
    BaseModel
):
    product_id: int

    sku: str
    product_name: str

    physical_quantity: int
    reserved_quantity: int
    sellable_quantity: int


class DashboardWarehouseItem(BaseModel):
    warehouse_id: int

    code: str
    name: str

    city: str
    province: str

    total_physical: int
    total_reserved: int
    total_sellable: int

    inventory: list[
        DashboardWarehouseInventoryItem
    ] = Field(
        default_factory=list
    )


class DashboardWarehouseListResponse(
    BaseModel
):
    items: list[DashboardWarehouseItem] = (
        Field(
            default_factory=list
        )
    )

    total: int


class DashboardApprovalItem(BaseModel):
    id: int

    thread_id: str
    status: str

    requested_by_user_id: int

    decided_by_user_id: int | None = None

    decision_comment: str | None = None

    created_at: datetime
    decided_at: datetime | None = None


class DashboardApprovalListResponse(
    BaseModel
):
    items: list[DashboardApprovalItem] = (
        Field(
            default_factory=list
        )
    )

    total: int


class DashboardActivityItem(BaseModel):
    id: int

    workflow_run_id: int
    thread_id: str

    operation: str
    username: str

    event_type: str
    node_name: str | None = None

    status: str

    message: str | None = None
    metadata_json: str | None = None

    created_at: datetime


class DashboardActivityListResponse(
    BaseModel
):
    items: list[DashboardActivityItem] = (
        Field(
            default_factory=list
        )
    )

    total: int