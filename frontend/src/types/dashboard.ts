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

export interface DashboardQuoteItem {
  id: number;
  thread_id: string;
  operation: string;

  user_id: number;
  username: string;
  user_role: string;

  status: string;
  current_node: string | null;
  requires_approval: boolean;

  error_type: string | null;
  error_message: string | null;

  retry_count: number;

  input_tokens: number;
  output_tokens: number;
  total_tokens: number;

  llm_latency_ms: number | null;
  duration_ms: number | null;

  started_at: string;
  completed_at: string | null;
}

export interface DashboardQuoteResponse {
  items: DashboardQuoteItem[];
  total: number;
}

export interface DashboardApprovalItem {
  id: number;
  thread_id: string;
  status: string;

  requested_by_user_id: number;
  decided_by_user_id: number | null;

  decision_comment: string | null;

  created_at: string;
  decided_at: string | null;
}

export interface DashboardApprovalResponse {
  items: DashboardApprovalItem[];
  total: number;
}

export interface DashboardActivityItem {
  id: number;
  workflow_run_id: number;

  thread_id: string;
  operation: string;
  username: string;

  event_type: string;
  node_name: string | null;
  status: string;

  message: string | null;
  metadata_json: string | null;

  created_at: string;
}

export interface DashboardActivityResponse {
  items: DashboardActivityItem[];
  total: number;
}