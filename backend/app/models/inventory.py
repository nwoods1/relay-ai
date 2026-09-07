from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            name="uq_inventory_product_warehouse"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id")
    )

    quantity_available: Mapped[int]
    quantity_reserved: Mapped[int] = mapped_column(default=0)

    product = relationship("Product")
    warehouse = relationship("Warehouse")