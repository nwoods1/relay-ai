from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    idempotency_key: str | None = None


class AgentAction(BaseModel):
    type: str
    data: dict[str, Any] | None = None


class AgentChatResponse(BaseModel):
    conversation_id: str
    message: str

    action: AgentAction | None = None

    workflow_thread_id: str | None = None

    awaiting_confirmation: bool = False

    selected_agent: str | None = None


class ConversationMessageResponse(BaseModel):
    role: str
    content: str
    message_type: str
    workflow_thread_id: str | None
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    conversation_id: str

    messages: list[
        ConversationMessageResponse
    ]