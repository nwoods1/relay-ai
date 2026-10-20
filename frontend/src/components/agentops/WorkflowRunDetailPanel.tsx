import type {
  WorkflowRunDetail,
} from "../../api/relay";


type WorkflowRunDetailPanelProps = {
  run:
    | WorkflowRunDetail
    | null;

  loading: boolean;

  onClose: () => void;
};


function formatDate(
  value: string
) {
  return new Date(
    value
  ).toLocaleString();
}


function formatDuration(
  value:
    | number
    | null
) {
  if (
    value === null
  ) {
    return "—";
  }

  if (
    value < 1000
  ) {
    return `${Math.round(
      value
    )} ms`;
  }

  return `${(
    value / 1000
  ).toFixed(2)} s`;
}


export default function WorkflowRunDetailPanel({
  run,
  loading,
  onClose,
}: WorkflowRunDetailPanelProps) {

  if (
    !run &&
    !loading
  ) {
    return null;
  }


  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/20 backdrop-blur-[2px]">
      <button
        type="button"
        aria-label="Close workflow details"
        onClick={
          onClose
        }
        className="absolute inset-0"
      />

      <aside className="relative h-full w-full max-w-xl overflow-y-auto border-l border-[#dce2d6] bg-[#f6f7f3] shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-[#dde2d8] bg-white/95 px-6 py-5 backdrop-blur">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8c9488]">
              Workflow trace
            </p>

            <h2 className="mt-1 text-lg font-semibold text-[#202b1d]">
              Run details
            </h2>
          </div>

          <button
            type="button"
            onClick={
              onClose
            }
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-[#dce1d7] bg-white text-[#697264] transition hover:bg-[#f3f5f0]"
          >
            ×
          </button>
        </div>


        {loading ? (
          <div className="flex min-h-[400px] items-center justify-center">
            <p className="text-sm text-[#788173]">
              Loading workflow...
            </p>
          </div>
        ) : run ? (
          <div className="space-y-5 p-6">

            <section className="rounded-[20px] border border-[#dde3d8] bg-white p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs text-[#8a9285]">
                    Thread ID
                  </p>

                  <p className="mt-1 break-all font-mono text-xs text-[#45523f]">
                    {run.thread_id}
                  </p>
                </div>

                <span className="rounded-full bg-[#edf3e8] px-3 py-1 text-xs font-medium text-[#55733e]">
                  {run.status.replaceAll(
                    "_",
                    " "
                  )}
                </span>
              </div>
            </section>


            <section className="grid grid-cols-2 gap-3">
              <div className="rounded-[18px] border border-[#dfe4da] bg-white p-4">
                <p className="text-xs text-[#8a9285]">
                  Operation
                </p>

                <p className="mt-1 text-sm font-medium text-[#35412f]">
                  {run.operation}
                </p>
              </div>

              <div className="rounded-[18px] border border-[#dfe4da] bg-white p-4">
                <p className="text-xs text-[#8a9285]">
                  Current node
                </p>

                <p className="mt-1 text-sm font-medium text-[#35412f]">
                  {run.current_node ??
                    "—"}
                </p>
              </div>

              <div className="rounded-[18px] border border-[#dfe4da] bg-white p-4">
                <p className="text-xs text-[#8a9285]">
                  Duration
                </p>

                <p className="mt-1 text-sm font-medium text-[#35412f]">
                  {formatDuration(
                    run.duration_ms
                  )}
                </p>
              </div>

              <div className="rounded-[18px] border border-[#dfe4da] bg-white p-4">
                <p className="text-xs text-[#8a9285]">
                  LLM latency
                </p>

                <p className="mt-1 text-sm font-medium text-[#35412f]">
                  {formatDuration(
                    run.llm_latency_ms
                  )}
                </p>
              </div>

              <div className="rounded-[18px] border border-[#dfe4da] bg-white p-4">
                <p className="text-xs text-[#8a9285]">
                  Tokens
                </p>

                <p className="mt-1 text-sm font-medium text-[#35412f]">
                  {run.total_tokens.toLocaleString()}
                </p>

                <p className="mt-1 text-[11px] text-[#8b9387]">
                  {run.input_tokens.toLocaleString()} in /{" "}
                  {run.output_tokens.toLocaleString()} out
                </p>
              </div>

              <div className="rounded-[18px] border border-[#dfe4da] bg-white p-4">
                <p className="text-xs text-[#8a9285]">
                  Retries
                </p>

                <p className="mt-1 text-sm font-medium text-[#35412f]">
                  {run.retry_count}
                </p>
              </div>
            </section>


            {(run.error_type ||
              run.error_message) && (
              <section className="rounded-[20px] border border-[#ecd8d4] bg-[#fbf3f1] p-5">
                <p className="text-xs font-medium uppercase tracking-[0.1em] text-[#a16258]">
                  Failure
                </p>

                {run.error_type && (
                  <p className="mt-2 text-sm font-semibold text-[#6f3e36]">
                    {run.error_type}
                  </p>
                )}

                {run.error_message && (
                  <p className="mt-2 text-sm leading-6 text-[#81564f]">
                    {run.error_message}
                  </p>
                )}
              </section>
            )}


            <section className="rounded-[20px] border border-[#dde3d8] bg-white p-5">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8a9285]">
                  Timeline
                </p>

                <h3 className="mt-1 text-base font-semibold text-[#273321]">
                  Workflow events
                </h3>
              </div>


              {run.events.length ===
              0 ? (
                <p className="mt-5 text-sm text-[#7b8377]">
                  No workflow events recorded.
                </p>
              ) : (
                <div className="mt-5 space-y-0">
                  {run.events.map(
                    (
                      event,
                      index
                    ) => (
                      <div
                        key={
                          event.id
                        }
                        className="relative flex gap-4 pb-6 last:pb-0"
                      >
                        {index <
                          run.events.length -
                            1 && (
                          <div className="absolute left-[7px] top-4 h-full w-px bg-[#dfe4da]" />
                        )}

                        <div className="relative z-[1] mt-1.5 h-[15px] w-[15px] shrink-0 rounded-full border-4 border-white bg-[#719451] shadow-[0_0_0_1px_#cad5c0]" />

                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-sm font-medium text-[#34412f]">
                              {event.event_type.replaceAll(
                                "_",
                                " "
                              )}
                            </p>

                            <span className="rounded-full bg-[#f1f4ee] px-2 py-0.5 text-[10px] font-medium text-[#687463]">
                              {event.status}
                            </span>
                          </div>

                          {event.node_name && (
                            <p className="mt-1 font-mono text-[11px] text-[#7e8878]">
                              {event.node_name}
                            </p>
                          )}

                          {event.message && (
                            <p className="mt-2 text-xs leading-5 text-[#747e6f]">
                              {event.message}
                            </p>
                          )}

                          <p className="mt-2 text-[10px] text-[#a0a69c]">
                            {formatDate(
                              event.created_at
                            )}
                          </p>
                        </div>
                      </div>
                    )
                  )}
                </div>
              )}
            </section>


            <section className="rounded-[20px] border border-[#dde3d8] bg-white p-5">
              <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8a9285]">
                Run metadata
              </p>

              <div className="mt-4 space-y-3 text-xs">
                <div className="flex justify-between gap-4">
                  <span className="text-[#858e81]">
                    User
                  </span>

                  <span className="font-medium text-[#45503f]">
                    {run.username}
                  </span>
                </div>

                <div className="flex justify-between gap-4">
                  <span className="text-[#858e81]">
                    Role
                  </span>

                  <span className="font-medium text-[#45503f]">
                    {run.user_role}
                  </span>
                </div>

                <div className="flex justify-between gap-4">
                  <span className="text-[#858e81]">
                    Approval required
                  </span>

                  <span className="font-medium text-[#45503f]">
                    {run.requires_approval
                      ? "Yes"
                      : "No"}
                  </span>
                </div>

                <div className="flex justify-between gap-4">
                  <span className="text-[#858e81]">
                    Started
                  </span>

                  <span className="text-right font-medium text-[#45503f]">
                    {formatDate(
                      run.started_at
                    )}
                  </span>
                </div>

                <div className="flex justify-between gap-4">
                  <span className="text-[#858e81]">
                    Completed
                  </span>

                  <span className="text-right font-medium text-[#45503f]">
                    {run.completed_at
                      ? formatDate(
                          run.completed_at
                        )
                      : "—"}
                  </span>
                </div>
              </div>
            </section>

          </div>
        ) : null}
      </aside>
    </div>
  );
}