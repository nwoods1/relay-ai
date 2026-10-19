import type {
  DashboardApprovalItem,
} from "../../types/dashboard";


interface ApprovalTableProps {
  items: DashboardApprovalItem[];

  actionLoadingThreadId:
    | string
    | null;

  onApprove: (
    approval: DashboardApprovalItem
  ) => void;

  onReject: (
    approval: DashboardApprovalItem
  ) => void;
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
  if (status === "pending") {
    return "bg-amber-100 text-amber-700";
  }

  if (status === "approved") {
    return "bg-emerald-100 text-emerald-700";
  }

  if (status === "rejected") {
    return "bg-red-100 text-red-700";
  }

  return "bg-slate-100 text-slate-700";
}


export default function ApprovalTable({
  items,
  actionLoadingThreadId,
  onApprove,
  onReject,
}: ApprovalTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm text-slate-500">
          No approval requests found.
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
                Requested By
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Status
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Requested
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Comment
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Actions
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {items.map(
              (approval) => {
                const isLoading =
                  actionLoadingThreadId ===
                  approval.thread_id;

                return (
                  <tr
                    key={approval.id}
                    className="hover:bg-slate-50"
                  >
                    <td className="max-w-[180px] px-5 py-4">
                      <span
                        className="block truncate font-mono text-xs text-slate-700"
                        title={
                          approval.thread_id
                        }
                      >
                        {
                          approval.thread_id
                        }
                      </span>
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-700">
                      User #
                      {
                        approval.requested_by_user_id
                      }
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${getStatusClassName(
                          approval.status
                        )}`}
                      >
                        {formatStatus(
                          approval.status
                        )}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-600">
                      {formatDate(
                        approval.created_at
                      )}
                    </td>

                    <td className="max-w-[220px] px-5 py-4 text-sm text-slate-600">
                      {approval.decision_comment ??
                        "—"}
                    </td>

                    <td className="px-5 py-4">
                      {approval.status ===
                      "pending" ? (
                        <div className="flex justify-end gap-2">
                          <button
                            type="button"
                            disabled={
                              isLoading
                            }
                            onClick={() =>
                              onReject(
                                approval
                              )
                            }
                            className="rounded-lg border border-red-200 bg-white px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            Reject
                          </button>

                          <button
                            type="button"
                            disabled={
                              isLoading
                            }
                            onClick={() =>
                              onApprove(
                                approval
                              )
                            }
                            className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            {isLoading
                              ? "Saving..."
                              : "Approve"}
                          </button>
                        </div>
                      ) : (
                        <div className="text-right text-sm text-slate-500">
                          {approval.decided_at
                            ? formatDate(
                                approval.decided_at
                              )
                            : "Complete"}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              }
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}