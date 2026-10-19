import type {
  AgentAction,
} from "../../api/relay";


type AssistantActionCardProps = {
  action:
    | AgentAction
    | null;

  threadId:
    | string
    | null;

  awaitingConfirmation:
    boolean;

  loading: boolean;

  onConfirm: () => void;

  onCancel: () => void;
};


function shortThreadId(
  threadId:
    | string
    | null
) {
  if (!threadId) {
    return null;
  }

  if (
    threadId.length <= 18
  ) {
    return threadId;
  }

  return (
    `${threadId.slice(0, 8)}`
    + "..."
    + `${threadId.slice(-6)}`
  );
}


export default function AssistantActionCard({
  action,
  threadId,
  awaitingConfirmation,
  loading,
  onConfirm,
  onCancel,
}: AssistantActionCardProps) {

  const actionType =
    action?.type ?? null;

  const displayThreadId =
    shortThreadId(
      threadId
    );


  if (
    awaitingConfirmation
  ) {
    return (
      <div className="mt-3 overflow-hidden rounded-2xl border border-[#d7dfcf] bg-[#f5f8f1]">
        <div className="border-b border-[#dfe6d8] px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#e1ead8] text-[#55733e]">
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  d="M12 9v4"
                />

                <path
                  d="M12 17h.01"
                />

                <path
                  d="M10.3 3.7 2.7 17a2 2 0 0 0 1.7 3h15.2a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z"
                />
              </svg>
            </div>

            <div>
              <p className="text-sm font-semibold text-[#263420]">
                Manager approval required
              </p>

              <p className="mt-0.5 text-xs text-[#74806e]">
                This workflow cannot continue until it is submitted for review.
              </p>
            </div>
          </div>
        </div>


        <div className="px-4 py-4">
          {displayThreadId && (
            <div className="mb-4 flex items-center justify-between rounded-xl bg-white px-3 py-2.5">
              <span className="text-xs text-[#828a7d]">
                Workflow
              </span>

              <span className="font-mono text-xs text-[#42503d]">
                {displayThreadId}
              </span>
            </div>
          )}


          <div className="flex flex-col gap-2 sm:flex-row">
            <button
              type="button"
              disabled={loading}
              onClick={
                onConfirm
              }
              className="flex-1 rounded-xl bg-[#719451] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#5f8244] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Submitting..."
                : "Submit for approval"}
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={
                onCancel
              }
              className="rounded-xl border border-[#d8dfd2] bg-white px-4 py-2.5 text-sm font-medium text-[#596554] transition hover:bg-[#f7f8f5] disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }


  if (
    actionType ===
    "approval_submitted"
  ) {
    return (
      <div className="mt-3 rounded-2xl border border-[#d8e2d0] bg-[#f3f7ef] p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#719451] text-white">
            <svg
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.3"
            >
              <path
                d="m5 12 4 4L19 6"
              />
            </svg>
          </div>

          <div>
            <p className="text-sm font-semibold text-[#283622]">
              Sent for approval
            </p>

            <p className="mt-1 text-xs leading-5 text-[#6e7968]">
              The quote is now waiting for a manager to review it.
            </p>

            {displayThreadId && (
              <p className="mt-2 font-mono text-[11px] text-[#879181]">
                {displayThreadId}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }


  if (
    actionType ===
    "approved"
  ) {
    return (
      <div className="mt-3 rounded-2xl border border-[#d8e2d0] bg-[#f3f7ef] p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#719451] text-white">
            <svg
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.3"
            >
              <path
                d="m5 12 4 4L19 6"
              />
            </svg>
          </div>

          <div>
            <p className="text-sm font-semibold text-[#283622]">
              Quote approved
            </p>

            <p className="mt-1 text-xs leading-5 text-[#6e7968]">
              The workflow has resumed successfully.
            </p>

            {displayThreadId && (
              <p className="mt-2 font-mono text-[11px] text-[#879181]">
                {displayThreadId}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }


  if (
    actionType ===
    "rejected"
  ) {
    return (
      <div className="mt-3 rounded-2xl border border-[#ead8d5] bg-[#fbf4f2] p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#b46a5e] text-white">
            <svg
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
            >
              <path
                d="M18 6 6 18"
              />

              <path
                d="m6 6 12 12"
              />
            </svg>
          </div>

          <div>
            <p className="text-sm font-semibold text-[#50312c]">
              Quote rejected
            </p>

            <p className="mt-1 text-xs leading-5 text-[#8b6b65]">
              The workflow has been closed.
            </p>

            {displayThreadId && (
              <p className="mt-2 font-mono text-[11px] text-[#9a7c76]">
                {displayThreadId}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }


  return null;
}