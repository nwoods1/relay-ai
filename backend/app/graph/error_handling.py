from app.monitoring.logger import logger


def build_failure_state(
    exc: Exception,
    node_name: str,
    retry_count: int | None = None,
) -> dict:

    logger.error(
        "Workflow failure node=%s error_type=%s error=%s",
        node_name,
        exc.__class__.__name__,
        str(exc),
    )

    return {
        "workflow_status": "failed",
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
        "failed_node": node_name,
        "retry_count": retry_count,
        "current_node": node_name,
    }