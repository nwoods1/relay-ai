from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    thread_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    operation: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100)
    )

    user_role: Mapped[str] = mapped_column(
        String(50)
    )

    status: Mapped[str] = mapped_column(
        String(50),
        index=True,
        default="running",
    )

    current_node: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    requires_approval: Mapped[bool] = (
        mapped_column(
            Boolean,
            default=False,
        )
    )

    error_type: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    input_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    llm_latency_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    duration_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    started_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow,
        )
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True,
    )