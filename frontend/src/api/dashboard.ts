import { apiRequest } from "./client";

import type {
  DashboardInventoryResponse,
  DashboardOverview,
  DashboardWarehouseResponse,
} from "../types/dashboard";

export async function getDashboardOverview() {
  return apiRequest<DashboardOverview>(
    "/dashboard/overview"
  );
}

export async function getDashboardInventory(
  search?: string
) {
  const params = new URLSearchParams();

  if (search?.trim()) {
    params.set(
      "search",
      search.trim()
    );
  }

  const query = params.toString();

  return apiRequest<DashboardInventoryResponse>(
    `/dashboard/inventory${
      query ? `?${query}` : ""
    }`
  );
}

export async function getDashboardWarehouses() {
  return apiRequest<DashboardWarehouseResponse>(
    "/dashboard/warehouses"
  );
}