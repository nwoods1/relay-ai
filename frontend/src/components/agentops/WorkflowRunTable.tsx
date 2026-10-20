import type {
  WorkflowRunSummary,
} from "../../api/relay";


type WorkflowRunTableProps = {
  runs:
    WorkflowRunSummary[];

  selectedThreadId:
    | string
    | null;

  onSelect: (
    threadId: string
  ) => void;
};


function formatDate(
  value: string
) {
  return new Date(
    value
  ).toLocaleString();
}


function formatDuration(
  duration:
    | number
    | null
) {
  if (
    duration === null
  ) {
    return "—";
  }

  if (
    duration < 1000
  ) {
    return `${Math.round(
      duration
    )} ms`;
  }

  return `${(
    duration / 1000
  ).toFixed(2)} s`;
}


function shortThreadId(
  threadId: string
) {
  if (
    threadId.length <= 16
  ) {
    return threadId;
  }

  return (
    `${threadId.slice(0, 7)}`
    + "..."
    + `${threadId.slice(-5)}`
  );
}


function statusClasses(
  status: string
) {
  const normalized =
    status.toLowerCase();

  if (
    normalized ===
      "ready" ||
    normalized ===
      "completed" ||
    normalized ===
      "approved"
  ) {
    return "bg-[#e9f1e4] text-[#54733e]";
  }

  if (
    normalized ===
      "failed" ||
    normalized ===
      "error"
  ) {
    return "bg-[#f8e8e4] text-[#9b5147]";
  }

  if (
    normalized ===
      "awaiting_approval"
  ) {
    return "bg-[#f5eddc] text-[#8a6a31]";
  }

  if (
    normalized ===
      "rejected"
  ) {
    return "bg-[#f2e5e2] text-[#875148]";
  }

  return "bg-[#edf0ea] text-[#677061]";
}


export default function WorkflowRunTable({
  runs,
  selectedThreadId,
  onSelect,
}: WorkflowRunTableProps) {

  if (
    runs.length === 0
  ) {
    return (
      <div className="rounded-[22px] border border-[#dce2d6] bg-white p-10 text-center">
        <p className="text-sm text-[#747d70]">
          No workflow runs found.
        </p>
      </div>
    );
  }


  return (
    <div className="overflow-hidden rounded-[22px] border border-[#dce2d6] bg-white shadow-[0_10px_28px_rgba(37,53,31,0.04)]">
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="border-b border-[#e4e8e0] bg-[#f7f8f5]">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Workflow
              </th>

              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-[#858d80]">
                User
              </th>

              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Operation
              </th>

              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Status
              </th>

              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Node
              </th>

              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Tokens
              </th>

              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Duration
              </th>

              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-[#858d80]">
                Started
              </th>
            </tr>
          </thead>


          <tbody className="divide-y divide-[#edf0e9]">
            {runs.map(
              (run) => {
                const selected =
                  selectedThreadId ===
                  run.thread_id;

                return (
                  <tr
                    key={
                      run.thread_id
                    }
                    onClick={() =>
                      onSelect(
                        run.thread_id
                      )
                    }
                    className={`cursor-pointer transition ${
                      selected
                        ? "bg-[#f0f5eb]"
                        : "hover:bg-[#fafbf9]"
                    }`}
                  >
                    <td className="px-4 py-4">
                      <p className="font-mono text-xs font-medium text-[#41503b]">
                        {shortThreadId(
                          run.thread_id
                        )}
                      </p>
                    </td>

                    <td className="px-4 py-4">
                      <p className="text-sm font-medium text-[#35402f]">
                        {run.username}
                      </p>

                      <p className="mt-0.5 text-xs text-[#92998e]">
                        {run.user_role}
                      </p>
                    </td>

                    <td className="px-4 py-4 text-sm text-[#505b4b]">
                      {run.operation}
                    </td>

                    <td className="px-4 py-4">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusClasses(
                          run.status
                        )}`}
                      >
                        {run.status.replaceAll(
                          "_",
                          " "
                        )}
                      </span>
                    </td>

                    <td className="px-4 py-4 text-xs text-[#6f786a]">
                      {run.current_node ??
                        "—"}
                    </td>

                    <td className="px-4 py-4 text-right text-sm text-[#566151]">
                      {run.total_tokens.toLocaleString()}
                    </td>

                    <td className="px-4 py-4 text-right text-sm text-[#566151]">
                      {formatDuration(
                        run.duration_ms
                      )}
                    </td>

                    <td className="whitespace-nowrap px-4 py-4 text-xs text-[#798274]">
                      {formatDate(
                        run.started_at
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