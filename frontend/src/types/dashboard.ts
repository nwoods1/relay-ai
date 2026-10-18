export interface DashboardOverview {
  total_products: number;
  total_customers: number;
  total_warehouses: number;

  total_physical_inventory: number;
  total_reserved_inventory: number;
  total_sellable_inventory: number;

  total_workflows: number;
  active_workflows: number;
  completed_workflows: number;
  failed_workflows: number;

  pending_approvals: number;
}

export interface DashboardInventoryItem {
  product_id: number;
  sku: string;
  product_name: string;
  category: string;
  unit_size: string;

  physical_quantity: number;
  reserved_quantity: number;
  sellable_quantity: number;
}

export interface DashboardInventoryResponse {
  items: DashboardInventoryItem[];
  total: number;
}

export interface DashboardWarehouseInventoryItem {
  product_id: number;
  sku: string;
  product_name: string;

  physical_quantity: number;
  reserved_quantity: number;
  sellable_quantity: number;
}

export interface DashboardWarehouse {
  warehouse_id: number;
  code: string;
  name: string;
  city: string;
  province: string;

  total_physical: number;
  total_reserved: number;
  total_sellable: number;

  inventory: DashboardWarehouseInventoryItem[];
}

export interface DashboardWarehouseResponse {
  items: DashboardWarehouse[];
  total: number;
}