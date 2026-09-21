import {
  useEffect,
  useState,
} from "react";

import {
  type AgentOpsSummary,
  type WorkflowRunSummary,
  getAgentOpsSummary,
  getWorkflowRuns,
} from "../api/agentops";


export default function AgentOps() {
  const [
    summary,
    setSummary,
  ] = useState<
    AgentOpsSummary | null
  >(null);

  const [
    runs,
    setRuns,
  ] = useState<
    WorkflowRunSummary[]
  >([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  async function loadData() {
    try {
      setLoading(true);
      setError(null);

      const [
        summaryData,
        runData,
      ] = await Promise.all([
        getAgentOpsSummary(),
        getWorkflowRuns(),
      ]);

      setSummary(
        summaryData
      );

      setRuns(
        runData
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load AgentOps"
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  if (loading) {
    return (
      <div className="p-6">
        Loading AgentOps...
      </div>
    );
  }


  if (error) {
    return (
      <div className="p-6">
        <p>{error}</p>

        <button
          onClick={loadData}
          className="mt-4 rounded-md border px-4 py-2"
        >
          Retry
        </button>
      </div>
    );
  }


  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-semibold">
          AgentOps
        </h1>

        <p className="text-sm text-muted-foreground">
          Monitor AI workflow execution,
          approvals, failures, and LLM usage.
        </p>
      </div>

      {summary && (
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-lg border p-4">
            <p className="text-sm text-muted-foreground">
              Total Runs
            </p>

            <p className="text-2xl font-semibold">
              {summary.total_runs}
            </p>
          </div>

          <div className="rounded-lg border p-4">
            <p className="text-sm text-muted-foreground">
              Failed Runs
            </p>

            <p className="text-2xl font-semibold">
              {summary.failed_runs}
            </p>
          </div>

          <div className="rounded-lg border p-4">
            <p className="text-sm text-muted-foreground">
              Awaiting Approval
            </p>

            <p className="text-2xl font-semibold">
              {
                summary
                  .awaiting_approval_runs
              }
            </p>
          </div>

          <div className="rounded-lg border p-4">
            <p className="text-sm text-muted-foreground">
              Total LLM Tokens
            </p>

            <p className="text-2xl font-semibold">
              {summary.total_tokens}
            </p>
          </div>
        </div>
      )}

      <div className="rounded-lg border">
        <div className="flex items-center justify-between border-b p-4">
          <h2 className="font-semibold">
            Workflow Runs
          </h2>

          <button
            onClick={loadData}
            className="rounded-md border px-3 py-2 text-sm"
          >
            Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="p-3">
                  Thread
                </th>

                <th className="p-3">
                  User
                </th>

                <th className="p-3">
                  Status
                </th>

                <th className="p-3">
                  Node
                </th>

                <th className="p-3">
                  Duration
                </th>

                <th className="p-3">
                  Tokens
                </th>
              </tr>
            </thead>

            <tbody>
              {runs.map(
                (run) => (
                  <tr
                    key={
                      run.thread_id
                    }
                    className="border-b"
                  >
                    <td className="max-w-[200px] truncate p-3 font-mono text-xs">
                      {
                        run.thread_id
                      }
                    </td>

                    <td className="p-3">
                      {
                        run.username
                      }
                    </td>

                    <td className="p-3">
                      {
                        run.status
                      }
                    </td>

                    <td className="p-3">
                      {
                        run.current_node
                        ?? "-"
                      }
                    </td>

                    <td className="p-3">
                      {
                        run.duration_ms
                        !== null
                          ? `${run.duration_ms.toFixed(0)} ms`
                          : "-"
                      }
                    </td>

                    <td className="p-3">
                      {
                        run.total_tokens
                      }
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}