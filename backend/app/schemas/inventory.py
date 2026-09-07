from pydantic import BaseModel


class WarehouseInventoryResponse(BaseModel):
    warehouse_code: str
    warehouse_name: str
    quantity_available: int
    quantity_reserved: int


class ProductInventoryResponse(BaseModel):
    sku: str
    product_name: str
    total_available: int
    warehouses: list[WarehouseInventoryResponse]