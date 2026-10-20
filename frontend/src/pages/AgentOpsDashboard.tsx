import {
  useEffect,
  useState,
} from "react";

import {
  getAgentOpsSummary,
  getWorkflowRun,
  getWorkflowRuns,
} from "../api/relay";

import type {
  AgentOpsSummary,
  WorkflowRunDetail,
  WorkflowRunSummary,
} from "../api/relay";

import DashboardLayout from "../components/dashboard/DashboardLayout";
import AgentOpsStatCard from "../components/agentops/AgentOpsStatCard";
import WorkflowRunDetailPanel from "../components/agentops/WorkflowRunDetailPanel";
import WorkflowRunTable from "../components/agentops/WorkflowRunTable";


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

  if (
    apiError?.status === 401
  ) {
    return "Your session has expired. Please log in again.";
  }

  if (
    apiError?.status === 403
  ) {
    return "You don't have permission to view AgentOps.";
  }

  if (
    apiError?.data?.detail &&
    typeof apiError.data
      .detail === "string"
  ) {
    return apiError.data.detail;
  }

  return "Unable to load AgentOps data.";
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


export default function AgentOpsDashboard() {

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
    selectedRun,
    setSelectedRun,
  ] = useState<
    WorkflowRunDetail | null
  >(null);

  const [
    selectedThreadId,
    setSelectedThreadId,
  ] = useState<
    string | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    detailLoading,
    setDetailLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  useEffect(() => {
    async function loadAgentOps() {
      try {
        setLoading(true);
        setError(null);

        const [
          summaryResponse,
          runsResponse,
        ] = await Promise.all([
          getAgentOpsSummary(),
          getWorkflowRuns(),
        ]);

        setSummary(
          summaryResponse
        );

        setRuns(
          runsResponse
        );

      } catch (error) {
        setError(
          getErrorMessage(
            error
          )
        );

      } finally {
        setLoading(false);
      }
    }

    void loadAgentOps();
  }, []);


  async function handleSelectRun(
    threadId: string
  ) {
    try {
      setSelectedThreadId(
        threadId
      );

      setSelectedRun(
        null
      );

      setDetailLoading(
        true
      );

      setError(null);

      const response =
        await getWorkflowRun(
          threadId
        );

      setSelectedRun(
        response
      );

    } catch (error) {
      setSelectedThreadId(
        null
      );

      setError(
        getErrorMessage(
          error
        )
      );

    } finally {
      setDetailLoading(
        false
      );
    }
  }


  function closeDetail() {
    setSelectedThreadId(
      null
    );

    setSelectedRun(
      null
    );

    setDetailLoading(
      false
    );
  }


  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[420px] items-center justify-center">
          <p className="text-sm text-[#778173]">
            Loading AgentOps...
          </p>
        </div>
      </DashboardLayout>
    );
  }


  if (
    error &&
    !summary
  ) {
    return (
      <DashboardLayout>
        <div className="rounded-[22px] border border-red-200 bg-red-50 p-6">
          <h2 className="font-semibold text-red-800">
            Unable to load AgentOps
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>
        </div>
      </DashboardLayout>
    );
  }


  return (
    <>
      <DashboardLayout>
        <div>

          <section>
            <p className="text-sm font-medium text-[#719451]">
              Monitoring
            </p>

            <h1 className="mt-1 text-3xl font-semibold tracking-[-0.04em] text-[#182116]">
              AgentOps
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[#70796b]">
              Monitor workflow health,
              AI usage, failures,
              latency, retries, and
              execution traces across
              Relay.
            </p>
          </section>


          {summary && (
            <>
              <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <AgentOpsStatCard
                  title="Total Workflows"
                  value={
                    summary.total_runs
                  }
                  description="All recorded Relay workflow runs."
                />

                <AgentOpsStatCard
                  title="Completed"
                  value={
                    summary.ready_runs
                  }
                  description="Workflows that completed and reached ready state."
                  tone="success"
                />

                <AgentOpsStatCard
                  title="Awaiting Approval"
                  value={
                    summary.awaiting_approval_runs
                  }
                  description="Workflows currently paused for human review."
                  tone="warning"
                />

                <AgentOpsStatCard
                  title="Failed"
                  value={
                    summary.failed_runs
                  }
                  description="Workflow runs that ended with an error."
                  tone={
                    summary.failed_runs >
                    0
                      ? "danger"
                      : "success"
                  }
                />
              </section>


              <section className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <AgentOpsStatCard
                  title="Approved"
                  value={
                    summary.approved_runs
                  }
                  description="Approval workflows approved by managers."
                  tone="success"
                />

                <AgentOpsStatCard
                  title="Rejected"
                  value={
                    summary.rejected_runs
                  }
                  description="Approval workflows rejected by managers."
                />

                <AgentOpsStatCard
                  title="Avg Duration"
                  value={
                    formatDuration(
                      summary.average_duration_ms
                    )
                  }
                  description="Average end-to-end workflow execution time."
                />

                <AgentOpsStatCard
                  title="Total Tokens"
                  value={
                    summary.total_tokens.toLocaleString()
                  }
                  description="Total LLM tokens recorded across workflows."
                />
              </section>
            </>
          )}


          {error && (
            <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}


          <section className="mt-10">
            <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-[#202b1d]">
                  Workflow Runs
                </h2>

                <p className="mt-1 text-sm text-[#7a8375]">
                  Select a workflow to
                  inspect its complete
                  execution trace.
                </p>
              </div>

              <p className="text-xs text-[#8d9589]">
                {runs.length} runs
              </p>
            </div>


            <WorkflowRunTable
              runs={
                runs
              }
              selectedThreadId={
                selectedThreadId
              }
              onSelect={(
                threadId
              ) =>
                void handleSelectRun(
                  threadId
                )
              }
            />
          </section>
        </div>
      </DashboardLayout>


      {(selectedThreadId ||
        selectedRun) && (
        <WorkflowRunDetailPanel
          run={
            selectedRun
          }
          loading={
            detailLoading
          }
          onClose={
            closeDetail
          }
        />
      )}
    </>
  );
}