from typing import Literal

from pydantic import BaseModel


class AgentIntent(BaseModel):
    intent: Literal[
        "create_quote",
        "check_inventory",
        "list_approvals",
        "approve_quote",
        "reject_quote",
        "confirm_action",
        "reject_action",
        "general",
    ]

    customer_name: str | None = None
    product_name: str | None = None
    quantity: int | None = None
    warehouse_name: str | None = None

    confirmation: bool | None = None

    # ----------------------------------
    # Basic contextual references
    # ----------------------------------

    reference_previous_customer: bool = False
    reference_previous_product: bool = False
    reference_previous_quantity: bool = False
    reference_previous_warehouse: bool = False

    # ----------------------------------
    # Richer Phase 15 references
    # ----------------------------------

    reference_other_customer: bool = False
    reference_other_product: bool = False
    reference_other_warehouse: bool = False

    # ----------------------------------
    # Approval references
    # ----------------------------------

    approval_thread_id: str | None = None
    approval_comment: str | None = None

    reference_previous_approval: bool = False