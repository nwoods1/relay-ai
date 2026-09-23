from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    conversation_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100)
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
    )

    pending_action: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    pending_thread_id: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    last_customer_name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    last_product_name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    last_quantity: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    last_approval_thread_id: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    last_approval_action: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True,
    )