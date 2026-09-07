from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(100))
    unit_size: Mapped[str] = mapped_column(String(50))
    base_price: Mapped[float] = mapped_column(Numeric(10, 2))