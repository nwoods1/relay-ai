from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.conversation_message import (
    ConversationMessage,
)


def get_or_create_conversation(
    db: Session,
    conversation_id: str | None,
    user_id: int,
    username: str,
) -> Conversation:

    if conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.conversation_id
                == conversation_id,
                Conversation.user_id
                == user_id,
            )
            .first()
        )

        if conversation:
            return conversation

    conversation = Conversation(
        conversation_id=str(uuid4()),
        user_id=user_id,
        username=username,
        status="active",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def add_message(
    db: Session,
    conversation: Conversation,
    role: str,
    content: str,
    message_type: str = "text",
    workflow_thread_id: str | None = None,
) -> ConversationMessage:

    message = ConversationMessage(
        conversation_id=conversation.id,
        role=role,
        content=content,
        message_type=message_type,
        workflow_thread_id=workflow_thread_id,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages(
    db: Session,
    conversation: Conversation,
) -> list[ConversationMessage]:

    return (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.conversation_id
            == conversation.id
        )
        .order_by(
            ConversationMessage.created_at.asc()
        )
        .all()
    )


def set_pending_action(
    db: Session,
    conversation: Conversation,
    action: str,
    thread_id: str,
):
    conversation.pending_action = action
    conversation.pending_thread_id = thread_id

    db.commit()
    db.refresh(conversation)


def clear_pending_action(
    db: Session,
    conversation: Conversation,
):
    conversation.pending_action = None
    conversation.pending_thread_id = None

    db.commit()
    db.refresh(conversation)