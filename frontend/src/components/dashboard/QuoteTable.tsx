import type {
  DashboardQuoteItem,
} from "../../types/dashboard";


interface QuoteTableProps {
  items: DashboardQuoteItem[];
}


function formatDate(
  value: string | null
) {
  if (!value) {
    return "—";
  }

  return new Date(
    value
  ).toLocaleString();
}


function formatStatus(
  status: string
) {
  return status
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


function getStatusClassName(
  status: string
) {
  if (
    status === "failed"
  ) {
    return "bg-red-100 text-red-700";
  }

  if (
    status ===
      "awaiting_approval" ||
    status === "pending"
  ) {
    return "bg-amber-100 text-amber-700";
  }

  if (
    status === "completed" ||
    status === "ready" ||
    status === "approved"
  ) {
    return "bg-emerald-100 text-emerald-700";
  }

  if (
    status === "rejected"
  ) {
    return "bg-slate-200 text-slate-700";
  }

  return "bg-blue-100 text-blue-700";
}


export default function QuoteTable({
  items,
}: QuoteTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm text-slate-500">
          No quote workflows found.
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
                Thread
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                User
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Operation
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Status
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Approval
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Started
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Retries
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Duration
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {items.map(
              (item) => (
                <tr
                  key={item.id}
                  className="hover:bg-slate-50"
                >
                  <td className="max-w-[180px] px-5 py-4 text-sm text-slate-700">
                    <span
                      className="block truncate font-mono text-xs"
                      title={
                        item.thread_id
                      }
                    >
                      {item.thread_id}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <p className="text-sm font-medium text-slate-900">
                      {item.username}
                    </p>

                    <p className="text-xs text-slate-500">
                      {item.user_role}
                    </p>
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-700">
                    {formatStatus(
                      item.operation
                    )}
                  </td>

                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${getStatusClassName(
                        item.status
                      )}`}
                    >
                      {formatStatus(
                        item.status
                      )}
                    </span>
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-700">
                    {item.requires_approval
                      ? "Required"
                      : "Not required"}
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-600">
                    {formatDate(
                      item.started_at
                    )}
                  </td>

                  <td className="px-5 py-4 text-right text-sm text-slate-700">
                    {
                      item.retry_count
                    }
                  </td>

                  <td className="px-5 py-4 text-right text-sm text-slate-700">
                    {item.duration_ms !==
                    null
                      ? `${Math.round(
                          item.duration_ms
                        )} ms`
                      : "—"}
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}