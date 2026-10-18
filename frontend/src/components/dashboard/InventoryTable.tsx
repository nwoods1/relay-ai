import type {
  DashboardInventoryItem,
} from "../../types/dashboard";

interface InventoryTableProps {
  items: DashboardInventoryItem[];
}

function getInventoryStatus(
  sellableQuantity: number
) {
  if (sellableQuantity === 0) {
    return {
      label: "Out of stock",
      className:
        "bg-red-100 text-red-700",
    };
  }

  if (sellableQuantity <= 10) {
    return {
      label: "Low stock",
      className:
        "bg-amber-100 text-amber-700",
    };
  }

  return {
    label: "Available",
    className:
      "bg-emerald-100 text-emerald-700",
  };
}

export default function InventoryTable({
  items,
}: InventoryTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm text-slate-500">
          No inventory matched your search.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
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

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Category
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Unit Size
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

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Status
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {items.map((item) => {
              const status =
                getInventoryStatus(
                  item.sellable_quantity
                );

              return (
                <tr
                  key={item.product_id}
                  className="hover:bg-slate-50"
                >
                  <td className="px-5 py-4">
                    <p className="font-medium text-slate-900">
                      {item.product_name}
                    </p>
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-600">
                    {item.sku}
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-600">
                    {item.category}
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-600">
                    {item.unit_size}
                  </td>

                  <td className="px-5 py-4 text-right text-sm text-slate-700">
                    {item.physical_quantity.toLocaleString()}
                  </td>

                  <td className="px-5 py-4 text-right text-sm text-slate-700">
                    {item.reserved_quantity.toLocaleString()}
                  </td>

                  <td className="px-5 py-4 text-right text-sm font-semibold text-slate-900">
                    {item.sellable_quantity.toLocaleString()}
                  </td>

                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${status.className}`}
                    >
                      {status.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}