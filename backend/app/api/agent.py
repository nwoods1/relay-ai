from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_permission,
)
from app.core.database import get_db
from app.models.conversation import (
    Conversation,
)
from app.models.user import User
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    ConversationHistoryResponse,
    ConversationMessageResponse,
)
from app.services.agent_service import (
    handle_agent_message,
)
from app.services.conversation_service import (
    get_messages,
)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


@router.post(
    "/chat",
    response_model=AgentChatResponse,
)
def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "quote:create"
        )
    ),
):
    return handle_agent_message(
        request=request,
        db=db,
        user=current_user,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=(
        ConversationHistoryResponse
    ),
)
def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "quote:create"
        )
    ),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id
            == conversation_id,
            Conversation.user_id
            == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=(
                "Conversation not found"
            ),
        )

    messages = get_messages(
        db=db,
        conversation=conversation,
    )

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[
            ConversationMessageResponse(
                role=message.role,
                content=message.content,
                message_type=(
                    message.message_type
                ),
                workflow_thread_id=(
                    message.workflow_thread_id
                ),
                created_at=(
                    message.created_at
                ),
            )
            for message in messages
        ],
    )