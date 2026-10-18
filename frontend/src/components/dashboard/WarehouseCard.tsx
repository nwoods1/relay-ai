import type {
  DashboardWarehouse,
} from "../../types/dashboard";

interface WarehouseCardProps {
  warehouse: DashboardWarehouse;
}

export default function WarehouseCard({
  warehouse,
}: WarehouseCardProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-5">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              {warehouse.name}
            </h3>

            <p className="text-sm text-slate-500">
              {warehouse.city}, {warehouse.province}
            </p>
          </div>

          <span className="mt-2 inline-flex w-fit rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 sm:mt-0">
            {warehouse.code}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-3 gap-3">
          <div className="rounded-lg bg-slate-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Physical
            </p>

            <p className="mt-1 text-xl font-semibold text-slate-900">
              {warehouse.total_physical.toLocaleString()}
            </p>
          </div>

          <div className="rounded-lg bg-slate-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Reserved
            </p>

            <p className="mt-1 text-xl font-semibold text-slate-900">
              {warehouse.total_reserved.toLocaleString()}
            </p>
          </div>

          <div className="rounded-lg bg-slate-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Sellable
            </p>

            <p className="mt-1 text-xl font-semibold text-slate-900">
              {warehouse.total_sellable.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Product
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                SKU
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Physical
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Reserved
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Sellable
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {warehouse.inventory.map((item) => (
              <tr
                key={`${warehouse.warehouse_id}-${item.product_id}`}
              >
                <td className="px-5 py-3 text-sm font-medium text-slate-900">
                  {item.product_name}
                </td>

                <td className="px-5 py-3 text-sm text-slate-500">
                  {item.sku}
                </td>

                <td className="px-5 py-3 text-right text-sm text-slate-700">
                  {item.physical_quantity.toLocaleString()}
                </td>

                <td className="px-5 py-3 text-right text-sm text-slate-700">
                  {item.reserved_quantity.toLocaleString()}
                </td>

                <td className="px-5 py-3 text-right text-sm font-semibold text-slate-900">
                  {item.sellable_quantity.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}