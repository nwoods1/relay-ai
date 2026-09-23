from pydantic import BaseModel


class AgentConversationContext(BaseModel):
    customer_name: str | None = None
    product_name: str | None = None
    quantity: int | None = None

    pending_action: str | None = None
    pending_thread_id: str | None = None