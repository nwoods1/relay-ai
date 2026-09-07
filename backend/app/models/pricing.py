from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pricing(Base):
    __tablename__ = "pricing"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    pricing_tier: Mapped[str] = mapped_column(String(20))

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2)
    )

    product = relationship("Product")