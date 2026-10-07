from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.workflow_event import (
    WorkflowEvent,
)
from app.models.workflow_run import (
    WorkflowRun,
)

from app.schemas.dashboard import (
    DashboardActivityItem,
    DashboardActivityListResponse,
    DashboardApprovalItem,
    DashboardApprovalListResponse,
    DashboardInventoryItem,
    DashboardInventoryListResponse,
    DashboardOverviewResponse,
    DashboardQuoteItem,
    DashboardQuoteListResponse,
    DashboardWarehouseInventoryItem,
    DashboardWarehouseItem,
    DashboardWarehouseListResponse,
)


TERMINAL_WORKFLOW_STATUSES = {
    "completed",
    "approved",
    "rejected",
}

ACTIVE_WORKFLOW_STATUSES = {
    "running",
    "awaiting_approval",
}

FAILED_WORKFLOW_STATUSES = {
    "failed",
}


def calculate_sellable_quantity(
    available: int,
    reserved: int,
) -> int:

    return max(
        available - reserved,
        0,
    )


def get_dashboard_overview(
    db: Session,
) -> DashboardOverviewResponse:

    total_products = (
        db.query(Product)
        .count()
    )

    total_customers = (
        db.query(Customer)
        .count()
    )

    total_warehouses = (
        db.query(Warehouse)
        .count()
    )

    inventory_records = (
        db.query(Inventory)
        .all()
    )

    total_physical_inventory = sum(
        record.quantity_available
        for record in inventory_records
    )

    total_reserved_inventory = sum(
        record.quantity_reserved
        for record in inventory_records
    )

    total_sellable_inventory = sum(
        calculate_sellable_quantity(
            available=(
                record.quantity_available
            ),
            reserved=(
                record.quantity_reserved
            ),
        )
        for record in inventory_records
    )

    workflow_runs = (
        db.query(WorkflowRun)
        .all()
    )

    total_workflows = len(
        workflow_runs
    )

    active_workflows = sum(
        1
        for workflow in workflow_runs
        if workflow.status
        in ACTIVE_WORKFLOW_STATUSES
    )

    completed_workflows = sum(
        1
        for workflow in workflow_runs
        if workflow.status
        in TERMINAL_WORKFLOW_STATUSES
    )

    failed_workflows = sum(
        1
        for workflow in workflow_runs
        if workflow.status
        in FAILED_WORKFLOW_STATUSES
    )

    pending_approvals = (
        db.query(Approval)
        .filter(
            Approval.status
            == "pending"
        )
        .count()
    )

    return DashboardOverviewResponse(
        total_products=total_products,
        total_customers=total_customers,
        total_warehouses=total_warehouses,

        total_physical_inventory=(
            total_physical_inventory
        ),
        total_reserved_inventory=(
            total_reserved_inventory
        ),
        total_sellable_inventory=(
            total_sellable_inventory
        ),

        total_workflows=(
            total_workflows
        ),
        active_workflows=(
            active_workflows
        ),
        completed_workflows=(
            completed_workflows
        ),
        failed_workflows=(
            failed_workflows
        ),

        pending_approvals=(
            pending_approvals
        ),
    )


def get_dashboard_quotes(
    db: Session,
    limit: int = 20,
    status: str | None = None,
) -> DashboardQuoteListResponse:

    query = db.query(
        WorkflowRun
    )

    if status:
        query = query.filter(
            WorkflowRun.status
            == status
        )

    total = query.count()

    workflow_runs = (
        query
        .order_by(
            WorkflowRun.started_at.desc()
        )
        .limit(limit)
        .all()
    )

    items = [
        DashboardQuoteItem(
            thread_id=workflow.thread_id,
            operation=workflow.operation,

            user_id=workflow.user_id,
            username=workflow.username,
            user_role=workflow.user_role,

            status=workflow.status,

            current_node=(
                workflow.current_node
            ),

            requires_approval=(
                workflow.requires_approval
            ),

            error_type=(
                workflow.error_type
            ),

            error_message=(
                workflow.error_message
            ),

            retry_count=(
                workflow.retry_count
            ),

            input_tokens=(
                workflow.input_tokens
            ),

            output_tokens=(
                workflow.output_tokens
            ),

            total_tokens=(
                workflow.total_tokens
            ),

            llm_latency_ms=(
                workflow.llm_latency_ms
            ),

            duration_ms=(
                workflow.duration_ms
            ),

            started_at=(
                workflow.started_at
            ),

            completed_at=(
                workflow.completed_at
            ),
        )
        for workflow
        in workflow_runs
    ]

    return DashboardQuoteListResponse(
        items=items,
        total=total,
    )


def get_dashboard_inventory(
    db: Session,
    search: str | None = None,
) -> DashboardInventoryListResponse:

    products = (
        db.query(Product)
        .order_by(
            Product.name.asc()
        )
        .all()
    )

    inventory_records = (
        db.query(Inventory)
        .all()
    )

    inventory_by_product: dict[
        int,
        list[Inventory],
    ] = {}

    for record in inventory_records:
        inventory_by_product.setdefault(
            record.product_id,
            [],
        ).append(
            record
        )

    items: list[
        DashboardInventoryItem
    ] = []

    normalized_search = (
        search.strip().lower()
        if search
        else None
    )

    for product in products:

        if normalized_search:
            searchable_text = (
                f"{product.name} "
                f"{product.sku} "
                f"{product.category}"
            ).lower()

            if (
                normalized_search
                not in searchable_text
            ):
                continue

        records = (
            inventory_by_product.get(
                product.id,
                [],
            )
        )

        physical_quantity = sum(
            record.quantity_available
            for record in records
        )

        reserved_quantity = sum(
            record.quantity_reserved
            for record in records
        )

        sellable_quantity = sum(
            calculate_sellable_quantity(
                available=(
                    record.quantity_available
                ),
                reserved=(
                    record.quantity_reserved
                ),
            )
            for record in records
        )

        items.append(
            DashboardInventoryItem(
                product_id=product.id,
                sku=product.sku,
                product_name=product.name,
                category=product.category,
                unit_size=product.unit_size,

                physical_quantity=(
                    physical_quantity
                ),

                reserved_quantity=(
                    reserved_quantity
                ),

                sellable_quantity=(
                    sellable_quantity
                ),
            )
        )

    return DashboardInventoryListResponse(
        items=items,
        total=len(items),
    )


def get_dashboard_warehouses(
    db: Session,
) -> DashboardWarehouseListResponse:

    warehouses = (
        db.query(Warehouse)
        .order_by(
            Warehouse.code.asc()
        )
        .all()
    )

    items: list[
        DashboardWarehouseItem
    ] = []

    for warehouse in warehouses:

        inventory_records = (
            db.query(Inventory)
            .filter(
                Inventory.warehouse_id
                == warehouse.id
            )
            .all()
        )

        warehouse_inventory: list[
            DashboardWarehouseInventoryItem
        ] = []

        total_physical = 0
        total_reserved = 0
        total_sellable = 0

        for record in inventory_records:

            product = (
                record.product
            )

            physical_quantity = (
                record.quantity_available
            )

            reserved_quantity = (
                record.quantity_reserved
            )

            sellable_quantity = (
                calculate_sellable_quantity(
                    available=(
                        physical_quantity
                    ),
                    reserved=(
                        reserved_quantity
                    ),
                )
            )

            total_physical += (
                physical_quantity
            )

            total_reserved += (
                reserved_quantity
            )

            total_sellable += (
                sellable_quantity
            )

            warehouse_inventory.append(
                DashboardWarehouseInventoryItem(
                    product_id=product.id,
                    sku=product.sku,

                    product_name=(
                        product.name
                    ),

                    physical_quantity=(
                        physical_quantity
                    ),

                    reserved_quantity=(
                        reserved_quantity
                    ),

                    sellable_quantity=(
                        sellable_quantity
                    ),
                )
            )

        items.append(
            DashboardWarehouseItem(
                warehouse_id=warehouse.id,

                code=warehouse.code,
                name=warehouse.name,

                city=warehouse.city,
                province=warehouse.province,

                total_physical=(
                    total_physical
                ),

                total_reserved=(
                    total_reserved
                ),

                total_sellable=(
                    total_sellable
                ),

                inventory=(
                    warehouse_inventory
                ),
            )
        )

    return DashboardWarehouseListResponse(
        items=items,
        total=len(items),
    )


def get_dashboard_approvals(
    db: Session,
    limit: int = 20,
    status: str | None = None,
) -> DashboardApprovalListResponse:

    query = db.query(
        Approval
    )

    if status:
        query = query.filter(
            Approval.status
            == status
        )

    total = query.count()

    approvals = (
        query
        .order_by(
            Approval.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    items = [
        DashboardApprovalItem(
            id=approval.id,

            thread_id=(
                approval.thread_id
            ),

            status=(
                approval.status
            ),

            requested_by_user_id=(
                approval
                .requested_by_user_id
            ),

            decided_by_user_id=(
                approval
                .decided_by_user_id
            ),

            decision_comment=(
                approval.decision_comment
            ),

            created_at=(
                approval.created_at
            ),

            decided_at=(
                approval.decided_at
            ),
        )
        for approval
        in approvals
    ]

    return DashboardApprovalListResponse(
        items=items,
        total=total,
    )


def get_dashboard_activity(
    db: Session,
    limit: int = 20,
    status: str | None = None,
) -> DashboardActivityListResponse:

    query = (
        db.query(
            WorkflowEvent,
            WorkflowRun,
        )
        .join(
            WorkflowRun,
            WorkflowEvent.workflow_run_id
            == WorkflowRun.id,
        )
    )

    if status:
        query = query.filter(
            WorkflowEvent.status
            == status
        )

    total = query.count()

    records = (
        query
        .order_by(
            WorkflowEvent.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    items = [
        DashboardActivityItem(
            id=event.id,

            workflow_run_id=(
                event.workflow_run_id
            ),

            thread_id=(
                workflow.thread_id
            ),

            operation=(
                workflow.operation
            ),

            username=(
                workflow.username
            ),

            event_type=(
                event.event_type
            ),

            node_name=(
                event.node_name
            ),

            status=(
                event.status
            ),

            message=(
                event.message
            ),

            metadata_json=(
                event.metadata_json
            ),

            created_at=(
                event.created_at
            ),
        )
        for (
            event,
            workflow,
        )
        in records
    ]

    return DashboardActivityListResponse(
        items=items,
        total=total,
    )