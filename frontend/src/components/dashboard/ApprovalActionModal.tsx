import {
  useState,
} from "react";

import type {
  DashboardApprovalItem,
} from "../../types/dashboard";


export type ApprovalDecision =
  | "approved"
  | "rejected";


interface ApprovalActionModalProps {
  approval:
    | DashboardApprovalItem
    | null;

  decision:
    | ApprovalDecision
    | null;

  loading: boolean;

  onClose: () => void;

  onConfirm: (
    comment: string
  ) => void;
}


export default function ApprovalActionModal({
  approval,
  decision,
  loading,
  onClose,
  onConfirm,
}: ApprovalActionModalProps) {
  const [
    comment,
    setComment,
  ] = useState("");



  if (
    !approval ||
    !decision
  ) {
    return null;
  }


  const isApprove =
    decision === "approved";


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
        <h2 className="text-xl font-semibold text-slate-900">
          {isApprove
            ? "Approve quote"
            : "Reject quote"}
        </h2>

        <p className="mt-2 text-sm text-slate-600">
          Thread:
        </p>

        <p className="mt-1 break-all font-mono text-xs text-slate-700">
          {
            approval.thread_id
          }
        </p>

        <label
          htmlFor="approval-comment"
          className="mt-5 block text-sm font-medium text-slate-700"
        >
          Decision comment
        </label>

        <textarea
          id="approval-comment"
          value={comment}
          onChange={(event) =>
            setComment(
              event.target.value
            )
          }
          rows={4}
          placeholder={
            isApprove
              ? "Optional approval note..."
              : "Explain why the quote is being rejected..."
          }
          className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
        />

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            disabled={loading}
            onClick={
              onClose
            }
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Cancel
          </button>

          <button
            type="button"
            disabled={loading}
            onClick={() =>
              onConfirm(
                comment.trim()
              )
            }
            className={`rounded-lg px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60 ${
              isApprove
                ? "bg-slate-900 hover:bg-slate-700"
                : "bg-red-600 hover:bg-red-700"
            }`}
          >
            {loading
              ? "Saving..."
              : isApprove
                ? "Approve quote"
                : "Reject quote"}
          </button>
        </div>
      </div>
    </div>
  );
}