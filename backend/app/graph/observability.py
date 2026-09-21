from app.core.database import SessionLocal
from app.monitoring.logger import logger
from app.services.agentops_service import (
    record_workflow_event,
    update_current_node,
)


def record_node_event(
    workflow_run_id: int | None,
    node_name: str,
    status: str,
    message: str | None = None,
    metadata: dict | None = None,
):
    if not workflow_run_id:
        return

    logger.info(
        (
            "workflow_run=%s "
            "node=%s "
            "status=%s"
        ),
        workflow_run_id,
        node_name,
        status,
    )

    db = SessionLocal()

    try:
        update_current_node(
            db=db,
            workflow_run_id=
                workflow_run_id,
            node_name=node_name,
        )

        record_workflow_event(
            db=db,
            workflow_run_id=
                workflow_run_id,
            event_type="node",
            node_name=node_name,
            status=status,
            message=message,
            metadata=metadata,
        )

    finally:
        db.close()