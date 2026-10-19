import type {
  DashboardActivityItem,
} from "../../types/dashboard";


interface ActivityTableProps {
  items: DashboardActivityItem[];
}


function formatDate(
  value: string
) {
  return new Date(
    value
  ).toLocaleString();
}


function formatText(
  value: string
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


export default function ActivityTable({
  items,
}: ActivityTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm text-slate-500">
          No recent workflow activity.
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
                Time
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                User
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Operation
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Event
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Node
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Status
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Message
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
                  <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">
                    {formatDate(
                      item.created_at
                    )}
                  </td>

                  <td className="px-5 py-4 text-sm font-medium text-slate-900">
                    {
                      item.username
                    }
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-700">
                    {formatText(
                      item.operation
                    )}
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-700">
                    {formatText(
                      item.event_type
                    )}
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-600">
                    {item.node_name
                      ? formatText(
                          item.node_name
                        )
                      : "—"}
                  </td>

                  <td className="px-5 py-4 text-sm text-slate-700">
                    {formatText(
                      item.status
                    )}
                  </td>

                  <td className="max-w-[300px] px-5 py-4 text-sm text-slate-600">
                    {
                      item.message ??
                      "—"
                    }
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