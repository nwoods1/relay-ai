from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    ProductInventoryResponse,
    WarehouseInventoryResponse,
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get(
    "/{sku}",
    response_model=ProductInventoryResponse
)
def get_product_inventory(
    sku: str,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.sku == sku)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    inventory_rows = (
        db.query(Inventory, Warehouse)
        .join(
            Warehouse,
            Inventory.warehouse_id == Warehouse.id
        )
        .filter(
            Inventory.product_id == product.id
        )
        .all()
    )

    warehouses = []

    total_available = 0

    for inventory, warehouse in inventory_rows:
        total_available += inventory.quantity_available

        warehouses.append(
            WarehouseInventoryResponse(
                warehouse_code=warehouse.code,
                warehouse_name=warehouse.name,
                quantity_available=inventory.quantity_available,
                quantity_reserved=inventory.quantity_reserved,
            )
        )

    return ProductInventoryResponse(
        sku=product.sku,
        product_name=product.name,
        total_available=total_available,
        warehouses=warehouses,
    )


@router.get(
    "/{sku}/{warehouse_code}",
    response_model=WarehouseInventoryResponse
)
def get_warehouse_inventory(
    sku: str,
    warehouse_code: str,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.sku == sku)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.code == warehouse_code)
        .first()
    )

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product.id,
            Inventory.warehouse_id == warehouse.id,
        )
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    return WarehouseInventoryResponse(
        warehouse_code=warehouse.code,
        warehouse_name=warehouse.name,
        quantity_available=inventory.quantity_available,
        quantity_reserved=inventory.quantity_reserved,
    )