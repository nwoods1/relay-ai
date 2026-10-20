import {
  useEffect,
  useState,
} from "react";

import {
  decideQuoteApproval,
  getDashboardActivity,
  getDashboardApprovals,
  getDashboardQuotes,
} from "../api/dashboard";

import ActivityTable from "../components/dashboard/ActivityTable";

import ApprovalActionModal, {
  type ApprovalDecision,
} from "../components/dashboard/ApprovalActionModal";

import ApprovalTable from "../components/dashboard/ApprovalTable";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import QuoteTable from "../components/dashboard/QuoteTable";

import type {
  DashboardActivityItem,
  DashboardApprovalItem,
  DashboardQuoteItem,
} from "../types/dashboard";


interface ApiError {
  status?: number;

  data?: {
    detail?: string;
  };
}


type OperationsData = {
  quotes:
    DashboardQuoteItem[];

  approvals:
    DashboardApprovalItem[];

  activity:
    DashboardActivityItem[];
};


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
    return "You don't have permission to view manager operations.";
  }

  if (
    apiError?.status === 404
  ) {
    return "The approval request could not be found.";
  }

  if (
    apiError?.status === 409
  ) {
    return (
      apiError.data?.detail ??
      "This approval can no longer be completed because its workflow state is unavailable."
    );
  }

  if (
    apiError?.status === 422
  ) {
    return "The approval request was invalid.";
  }

  if (
    apiError?.data?.detail &&
    typeof apiError.data
      .detail === "string"
  ) {
    return apiError.data.detail;
  }

  return "Unable to complete the request.";
}


async function fetchOperationsData(
  approvalStatus: string
): Promise<OperationsData> {
  const [
    quoteResponse,
    approvalResponse,
    activityResponse,
  ] = await Promise.all([
    getDashboardQuotes({
      limit: 20,
    }),

    getDashboardApprovals({
      limit: 20,
      status:
        approvalStatus ||
        undefined,
    }),

    getDashboardActivity({
      limit: 30,
    }),
  ]);

  return {
    quotes:
      quoteResponse.items,

    approvals:
      approvalResponse.items,

    activity:
      activityResponse.items,
  };
}


export default function OperationsDashboard() {
  const [
    quotes,
    setQuotes,
  ] = useState<
    DashboardQuoteItem[]
  >([]);

  const [
    approvals,
    setApprovals,
  ] = useState<
    DashboardApprovalItem[]
  >([]);

  const [
    activity,
    setActivity,
  ] = useState<
    DashboardActivityItem[]
  >([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    successMessage,
    setSuccessMessage,
  ] = useState<
    string | null
  >(null);

  const [
    approvalStatus,
    setApprovalStatus,
  ] = useState(
    "pending"
  );

  const [
    selectedApproval,
    setSelectedApproval,
  ] = useState<
    DashboardApprovalItem | null
  >(null);

  const [
    selectedDecision,
    setSelectedDecision,
  ] = useState<
    ApprovalDecision | null
  >(null);

  const [
    actionLoadingThreadId,
    setActionLoadingThreadId,
  ] = useState<
    string | null
  >(null);


  useEffect(() => {
    let cancelled = false;

    void fetchOperationsData(
      approvalStatus
    )
      .then((data) => {
        if (cancelled) {
          return;
        }

        setQuotes(
          data.quotes
        );

        setApprovals(
          data.approvals
        );

        setActivity(
          data.activity
        );

        setError(null);
      })
      .catch((error) => {
        if (cancelled) {
          return;
        }

        setError(
          getErrorMessage(
            error
          )
        );
      })
      .finally(() => {
        if (
          !cancelled
        ) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [
    approvalStatus,
  ]);


  async function refreshOperations() {
    try {
      setRefreshing(true);
      setError(null);

      const data =
        await fetchOperationsData(
          approvalStatus
        );

      setQuotes(
        data.quotes
      );

      setApprovals(
        data.approvals
      );

      setActivity(
        data.activity
      );

    } catch (error) {
      setError(
        getErrorMessage(
          error
        )
      );

    } finally {
      setRefreshing(false);
    }
  }


  function openApprovalModal(
    approval:
      DashboardApprovalItem,
    decision:
      ApprovalDecision
  ) {
    setError(null);

    setSuccessMessage(
      null
    );

    setSelectedApproval(
      approval
    );

    setSelectedDecision(
      decision
    );
  }


  function closeApprovalModal() {
    if (
      actionLoadingThreadId
    ) {
      return;
    }

    setSelectedApproval(
      null
    );

    setSelectedDecision(
      null
    );
  }


  async function handleApprovalConfirm(
    comment: string
  ) {
    if (
      !selectedApproval ||
      !selectedDecision
    ) {
      return;
    }

    const threadId =
      selectedApproval.thread_id;

    const decision =
      selectedDecision;

    try {
      setActionLoadingThreadId(
        threadId
      );

      setError(null);

      setSuccessMessage(
        null
      );

      await decideQuoteApproval(
        threadId,
        decision,
        comment
      );

      setSelectedApproval(
        null
      );

      setSelectedDecision(
        null
      );

      setSuccessMessage(
        decision === "approved"
          ? "Quote approved successfully."
          : "Quote rejected successfully."
      );

      await refreshOperations();

    } catch (error) {
      setError(
        getErrorMessage(
          error
        )
      );

    } finally {
      setActionLoadingThreadId(
        null
      );
    }
  }


  function handleApprovalStatusChange(
    value: string
  ) {
    setSuccessMessage(
      null
    );

    setError(null);

    setApprovalStatus(
      value
    );
  }


  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[400px] items-center justify-center">
          <p className="text-sm text-[#778173]">
            Loading manager operations...
          </p>
        </div>
      </DashboardLayout>
    );
  }


  if (
    error &&
    quotes.length === 0 &&
    approvals.length === 0 &&
    activity.length === 0
  ) {
    return (
      <DashboardLayout>
        <div className="rounded-[22px] border border-red-200 bg-red-50 p-6">
          <h2 className="font-semibold text-red-800">
            Unable to load operations
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
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-medium text-[#719451]">
              Manager Operations
            </p>

            <h1 className="mt-1 text-3xl font-semibold tracking-[-0.04em] text-[#182116]">
              Quotes & Approvals
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[#70796b]">
              Review quote workflows,
              manage approval requests,
              and inspect recent workflow
              activity.
            </p>
          </div>


          <button
            type="button"
            disabled={
              refreshing
            }
            onClick={() => {
              setSuccessMessage(
                null
              );

              void refreshOperations();
            }}
            className="w-fit rounded-xl border border-[#d9ded4] bg-white px-4 py-2.5 text-sm font-medium text-[#33402e] shadow-sm transition hover:bg-[#f7f8f5] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>


        {successMessage && (
          <div className="mt-6 rounded-xl border border-[#d4e2cb] bg-[#f1f7ec] p-4 text-sm text-[#55733e]">
            {successMessage}
          </div>
        )}


        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}


        <section className="mt-10">
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-[#202b1d]">
                Approvals
              </h2>

              <p className="mt-1 text-sm text-[#7a8375]">
                Review quote requests
                that require manager
                approval.
              </p>
            </div>


            <div>
              <label
                htmlFor="approval-status"
                className="mb-1 block text-xs font-medium uppercase tracking-[0.1em] text-[#858d80]"
              >
                Status
              </label>

              <select
                id="approval-status"
                value={
                  approvalStatus
                }
                disabled={
                  refreshing
                }
                onChange={(
                  event
                ) =>
                  handleApprovalStatusChange(
                    event.target.value
                  )
                }
                className="rounded-xl border border-[#d9dfd3] bg-white px-3 py-2 text-sm text-[#45503f] outline-none transition focus:border-[#8aac69] focus:ring-4 focus:ring-[#8aac69]/10 disabled:opacity-60"
              >
                <option value="pending">
                  Pending
                </option>

                <option value="approved">
                  Approved
                </option>

                <option value="rejected">
                  Rejected
                </option>

                <option value="">
                  All
                </option>
              </select>
            </div>
          </div>


          <ApprovalTable
            items={
              approvals
            }
            actionLoadingThreadId={
              actionLoadingThreadId
            }
            onApprove={(
              approval
            ) =>
              openApprovalModal(
                approval,
                "approved"
              )
            }
            onReject={(
              approval
            ) =>
              openApprovalModal(
                approval,
                "rejected"
              )
            }
          />
        </section>


        <section className="mt-12">
          <div className="mb-5">
            <h2 className="text-xl font-semibold text-[#202b1d]">
              Recent Quotes
            </h2>

            <p className="mt-1 text-sm text-[#7a8375]">
              Recent quote workflow
              runs and their current
              status.
            </p>
          </div>

          <QuoteTable
            items={
              quotes
            }
          />
        </section>


        <section className="mt-12">
          <div className="mb-5">
            <h2 className="text-xl font-semibold text-[#202b1d]">
              Recent Activity
            </h2>

            <p className="mt-1 text-sm text-[#7a8375]">
              Recent workflow events
              across Relay AI.
            </p>
          </div>

          <ActivityTable
            items={
              activity
            }
          />
        </section>
      </div>


      <ApprovalActionModal
        approval={
          selectedApproval
        }
        decision={
          selectedDecision
        }
        loading={
          actionLoadingThreadId !==
          null
        }
        onClose={
          closeApprovalModal
        }
        onConfirm={
          handleApprovalConfirm
        }
      />
    </DashboardLayout>
  );
}