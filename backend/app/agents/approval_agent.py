from sqlalchemy.orm import Session

from app.models.approval import Approval


def list_pending_approvals(
    db: Session,
) -> list[Approval]:

    return (
        db.query(Approval)
        .filter(
            Approval.status
            == "pending"
        )
        .order_by(
            Approval.created_at.asc()
        )
        .all()
    )