import {
  useEffect,
  useState,
} from "react";

import {
  getDashboardInventory,
  getDashboardOverview,
  getDashboardWarehouses,
} from "../api/dashboard";

import DashboardLayout from "../components/dashboard/DashboardLayout";
import InventoryStatCard from "../components/dashboard/InventoryStatCard";
import InventoryTable from "../components/dashboard/InventoryTable";
import WarehouseCard from "../components/dashboard/WarehouseCard";

import type {
  DashboardInventoryItem,
  DashboardOverview,
  DashboardWarehouse,
} from "../types/dashboard";

interface ApiError {
  status?: number;
  data?: {
    detail?: string;
  };
}

function getErrorMessage(
  error: unknown
) {
  const apiError =
    error as ApiError;

  if (apiError?.status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (apiError?.status === 403) {
    return "You don't have permission to view the operations dashboard.";
  }

  if (
    apiError?.data?.detail &&
    typeof apiError.data.detail ===
      "string"
  ) {
    return apiError.data.detail;
  }

  return "Unable to load inventory data.";
}

export default function InventoryDashboard() {
  const [
    overview,
    setOverview,
  ] =
    useState<DashboardOverview | null>(
      null
    );

  const [
    inventory,
    setInventory,
  ] = useState<
    DashboardInventoryItem[]
  >([]);

  const [
    warehouses,
    setWarehouses,
  ] = useState<
    DashboardWarehouse[]
  >([]);

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    searching,
    setSearching,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [
          overviewResponse,
          inventoryResponse,
          warehouseResponse,
        ] = await Promise.all([
          getDashboardOverview(),
          getDashboardInventory(),
          getDashboardWarehouses(),
        ]);

        setOverview(
          overviewResponse
        );

        setInventory(
          inventoryResponse.items
        );

        setWarehouses(
          warehouseResponse.items
        );
      } catch (error) {
        setError(
          getErrorMessage(error)
        );
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);

  async function handleSearch() {
    try {
      setSearching(true);
      setError(null);

      const response =
        await getDashboardInventory(
          search
        );

      setInventory(
        response.items
      );
    } catch (error) {
      setError(
        getErrorMessage(error)
      );
    } finally {
      setSearching(false);
    }
  }

  async function handleClearSearch() {
    setSearch("");

    try {
      setSearching(true);
      setError(null);

      const response =
        await getDashboardInventory();

      setInventory(
        response.items
      );
    } catch (error) {
      setError(
        getErrorMessage(error)
      );
    } finally {
      setSearching(false);
    }
  }

  function handleSearchSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    void handleSearch();
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[400px] items-center justify-center">
          <p className="text-sm text-slate-500">
            Loading inventory...
          </p>
        </div>
      </DashboardLayout>
    );
  }

  if (error && !overview) {
    return (
      <DashboardLayout>
        <div className="rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="font-semibold text-red-800">
            Unable to load dashboard
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div>
        <div>
          <p className="text-sm font-medium text-slate-500">
            Operations
          </p>

          <h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            Inventory & Warehouses
          </h2>

          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            View product availability,
            reserved inventory, sellable
            stock, and warehouse-level
            inventory across the business.
          </p>
        </div>

        {overview && (
          <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <InventoryStatCard
              title="Products"
              value={
                overview.total_products
              }
              description="Products in the catalog"
            />

            <InventoryStatCard
              title="Physical Inventory"
              value={
                overview.total_physical_inventory
              }
              description="Total units physically available"
            />

            <InventoryStatCard
              title="Reserved Inventory"
              value={
                overview.total_reserved_inventory
              }
              description="Units already reserved"
            />

            <InventoryStatCard
              title="Sellable Inventory"
              value={
                overview.total_sellable_inventory
              }
              description="Units currently available to sell"
            />
          </section>
        )}

        <section className="mt-10">
          <div className="mb-4">
            <h3 className="text-xl font-semibold text-slate-900">
              Product Inventory
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Search inventory by
              product name, SKU, or
              category.
            </p>
          </div>

          <form
            onSubmit={
              handleSearchSubmit
            }
            className="mb-5 flex flex-col gap-3 sm:flex-row"
          >
            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search inventory..."
              className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
            />

            <button
              type="submit"
              disabled={searching}
              className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {searching
                ? "Searching..."
                : "Search"}
            </button>

            <button
              type="button"
              onClick={() =>
                void handleClearSearch()
              }
              disabled={searching}
              className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Clear
            </button>
          </form>

          {error && (
            <div className="mb-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <InventoryTable
            items={inventory}
          />
        </section>

        <section className="mt-12">
          <div className="mb-5">
            <h3 className="text-xl font-semibold text-slate-900">
              Warehouses
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Inventory totals and
              product availability by
              warehouse.
            </p>
          </div>

          {warehouses.length ===
          0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
              <p className="text-sm text-slate-500">
                No warehouse data is
                available.
              </p>
            </div>
          ) : (
            <div className="grid gap-6">
              {warehouses.map(
                (warehouse) => (
                  <WarehouseCard
                    key={
                      warehouse.warehouse_id
                    }
                    warehouse={
                      warehouse
                    }
                  />
                )
              )}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}