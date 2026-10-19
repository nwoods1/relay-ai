import {
  apiRequest,
} from "./client";

import type {
  DashboardActivityResponse,
  DashboardApprovalResponse,
  DashboardInventoryResponse,
  DashboardOverview,
  DashboardQuoteResponse,
  DashboardWarehouseResponse,
} from "../types/dashboard";


export type ApprovalDecision =
  | "approved"
  | "rejected";


export interface ApprovalDecisionRequest {
  decision: ApprovalDecision;
  comment: string | null;
}


export async function getDashboardOverview() {
  return apiRequest<DashboardOverview>(
    "/dashboard/overview"
  );
}


export async function getDashboardInventory(
  search?: string
) {
  const params =
    new URLSearchParams();

  if (search?.trim()) {
    params.set(
      "search",
      search.trim()
    );
  }

  const query =
    params.toString();

  return apiRequest<DashboardInventoryResponse>(
    `/dashboard/inventory${
      query
        ? `?${query}`
        : ""
    }`
  );
}


export async function getDashboardWarehouses() {
  return apiRequest<DashboardWarehouseResponse>(
    "/dashboard/warehouses"
  );
}


export async function getDashboardQuotes(
  options?: {
    limit?: number;
    status?: string;
  }
) {
  const params =
    new URLSearchParams();

  if (options?.limit) {
    params.set(
      "limit",
      String(options.limit)
    );
  }

  if (
    options?.status?.trim()
  ) {
    params.set(
      "status",
      options.status.trim()
    );
  }

  const query =
    params.toString();

  return apiRequest<DashboardQuoteResponse>(
    `/dashboard/quotes${
      query
        ? `?${query}`
        : ""
    }`
  );
}


export async function getDashboardApprovals(
  options?: {
    limit?: number;
    status?: string;
  }
) {
  const params =
    new URLSearchParams();

  if (options?.limit) {
    params.set(
      "limit",
      String(options.limit)
    );
  }

  if (
    options?.status?.trim()
  ) {
    params.set(
      "status",
      options.status.trim()
    );
  }

  const query =
    params.toString();

  return apiRequest<DashboardApprovalResponse>(
    `/dashboard/approvals${
      query
        ? `?${query}`
        : ""
    }`
  );
}


export async function getDashboardActivity(
  options?: {
    limit?: number;
    status?: string;
  }
) {
  const params =
    new URLSearchParams();

  if (options?.limit) {
    params.set(
      "limit",
      String(options.limit)
    );
  }

  if (
    options?.status?.trim()
  ) {
    params.set(
      "status",
      options.status.trim()
    );
  }

  const query =
    params.toString();

  return apiRequest<DashboardActivityResponse>(
    `/dashboard/activity${
      query
        ? `?${query}`
        : ""
    }`
  );
}


export async function decideQuoteApproval(
  threadId: string,
  decision: ApprovalDecision,
  comment: string
) {
  const requestBody:
    ApprovalDecisionRequest = {
      decision,
      comment:
        comment.trim() || null,
    };

  return apiRequest(
    `/approvals/${encodeURIComponent(
      threadId
    )}`,
    {
      method: "POST",

      headers: {
        "Idempotency-Key":
          crypto.randomUUID(),
      },

      body: JSON.stringify(
        requestBody
      ),
    }
  );
}