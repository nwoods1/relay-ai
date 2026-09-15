from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    thread_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )

    requested_by_user_id: Mapped[int] = (
        mapped_column(
            ForeignKey("users.id")
        )
    )

    decided_by_user_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    decision_comment: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow,
        )
    )

    decided_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True,
    )