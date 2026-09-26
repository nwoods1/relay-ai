from typing import Any

from pydantic import BaseModel


class AgentConversationContext(BaseModel):
    customer_name: str | None = None
    product_name: str | None = None
    quantity: int | None = None
    warehouse_name: str | None = None

    pending_action: str | None = None
    pending_thread_id: str | None = None

    last_approval_thread_id: str | None = None
    last_approval_action: str | None = None

    recent_customers: list[str] = []
    recent_products: list[str] = []
    recent_quantities: list[int] = []
    recent_warehouses: list[str] = []

    recent_actions: list[
        dict[str, Any]
    ] = []

    conversation_summary: str | None = None