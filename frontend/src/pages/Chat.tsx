import {
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  chatWithRelay,
  type AgentAction,
  type UserResponse,
} from "../api/relay";

import AssistantActionCard from "../components/chat/AssistantActionCard";
import ChatMessage from "../components/chat/ChatMessage";
import QuickActions from "../components/chat/QuickActions";


type Message = {
  role:
    | "user"
    | "assistant";

  content: string;

  action?:
    | AgentAction
    | null;

  workflowThreadId?:
    | string
    | null;

  awaitingConfirmation?:
    boolean;
};


type ChatProps = {
  user: UserResponse;
};


export default function Chat({
  user,
}: ChatProps) {
  const [
    messages,
    setMessages,
  ] = useState<
    Message[]
  >([]);

  const [
    input,
    setInput,
  ] = useState("");

  const [
    conversationId,
    setConversationId,
  ] = useState<
    string | null
  >(null);

  const [
    selectedAgent,
    setSelectedAgent,
  ] = useState<
    string | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    showDeveloperDetails,
    setShowDeveloperDetails,
  ] = useState(false);

  const messagesEndRef =
    useRef<
      HTMLDivElement | null
    >(null);


  useEffect(() => {
    messagesEndRef.current
      ?.scrollIntoView({
        behavior:
          "smooth",
      });
  }, [
    messages,
    loading,
  ]);


  async function sendMessage(
    text: string
  ) {
    const trimmed =
      text.trim();

    if (
      !trimmed ||
      loading
    ) {
      return;
    }

    setMessages(
      (current) => [
        ...current,
        {
          role:
            "user",
          content:
            trimmed,
        },
      ]
    );

    setInput("");
    setError(null);
    setLoading(true);

    try {
      const response =
        await chatWithRelay(
          trimmed,
          conversationId,
          crypto.randomUUID()
        );

      setConversationId(
        response.conversation_id
      );

      setSelectedAgent(
        response.selected_agent
      );

      setMessages(
        (current) => [
          ...current,
          {
            role:
              "assistant",

            content:
              response.message,

            action:
              response.action,

            workflowThreadId:
              response.workflow_thread_id,

            awaitingConfirmation:
              response.awaiting_confirmation,
          },
        ]
      );

    } catch (err) {
      console.error(
        err
      );

      setError(
        "Relay couldn't complete that request. Check the backend terminal for details."
      );

    } finally {
      setLoading(false);
    }
  }


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    await sendMessage(
      input
    );
  }


  function newConversation() {
    setConversationId(
      null
    );

    setSelectedAgent(
      null
    );

    setMessages([]);

    setInput("");

    setError(null);

    setShowDeveloperDetails(
      false
    );
  }


  const roleLabel =
    user.role
      .replaceAll(
        "_",
        " "
      )
      .replace(
        /\b\w/g,
        (letter) =>
          letter.toUpperCase()
      );


  return (
    <main className="min-h-[calc(100vh-70px)] bg-[#eef0eb] px-5 py-7 sm:px-7 lg:px-9">
      <div className="mx-auto max-w-[1440px]">

        <section className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-medium text-[#719451]">
              Relay Workspace
            </p>

            <h1 className="mt-1 text-3xl font-semibold tracking-[-0.04em] text-[#182116] sm:text-4xl">
              Good to see you,{" "}
              {user.username}.
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[#70796b]">
              Ask Relay to check
              inventory, create
              quotes, review
              approvals, or help
              with business
              operations.
            </p>
          </div>

          <button
            type="button"
            onClick={
              newConversation
            }
            className="w-fit rounded-xl border border-[#d9ded4] bg-white px-4 py-2.5 text-sm font-medium text-[#33402e] shadow-sm transition hover:bg-[#f7f8f5]"
          >
            + New conversation
          </button>
        </section>


        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_360px]">

          <section className="flex min-h-[680px] flex-col overflow-hidden rounded-[24px] border border-[#dfe3da] bg-[#f7f8f5] shadow-[0_14px_40px_rgba(37,53,31,0.06)]">

            <div className="flex items-center justify-between border-b border-[#e1e5dc] bg-white px-5 py-4 sm:px-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#719451] font-semibold text-white">
                  R
                </div>

                <div>
                  <h2 className="text-sm font-semibold text-[#1c2719]">
                    Relay Assistant
                  </h2>

                  <div className="mt-0.5 flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-[#76a257]" />

                    <span className="text-xs text-[#7d8578]">
                      Ready to help
                    </span>
                  </div>
                </div>
              </div>

              <span className="rounded-full bg-[#edf3e8] px-3 py-1 text-xs font-medium text-[#55733e]">
                Enterprise AI
              </span>
            </div>


            <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-6">

              {messages.length ===
              0 ? (
                <div className="flex h-full min-h-[380px] flex-col items-center justify-center text-center">

                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#719451] text-xl font-semibold text-white shadow-sm">
                    R
                  </div>

                  <h3 className="mt-5 text-xl font-semibold text-[#1c2719]">
                    What can I help
                    with?
                  </h3>

                  <p className="mt-2 max-w-md text-sm leading-6 text-[#788173]">
                    Relay connects
                    conversational AI
                    with your business
                    data, rules,
                    permissions and
                    approval workflows.
                  </p>

                  <div className="mt-6">
                    <QuickActions
                      disabled={
                        loading
                      }
                      userRole={
                        user.role
                      }
                      onAction={(
                        message
                      ) =>
                        void sendMessage(
                          message
                        )
                      }
                    />
                  </div>
                </div>
              ) : (

                <div className="space-y-5">

                  {messages.map(
                    (
                      message,
                      index
                    ) => (
                      <div
                        key={
                          index
                        }
                      >
                        <ChatMessage
                          role={
                            message.role
                          }
                          content={
                            message.content
                          }
                        />

                        {message.role ===
                          "assistant" && (
                          <div className="ml-9 max-w-[82%]">
                            <AssistantActionCard
                              action={
                                message.action ??
                                null
                              }
                              threadId={
                                message.workflowThreadId ??
                                null
                              }
                              awaitingConfirmation={
                                message.awaitingConfirmation ??
                                false
                              }
                              loading={
                                loading
                              }
                              onConfirm={() =>
                                void sendMessage(
                                  "yes"
                                )
                              }
                              onCancel={() =>
                                void sendMessage(
                                  "no"
                                )
                              }
                            />
                          </div>
                        )}
                      </div>
                    )
                  )}


                  {loading && (
                    <div className="flex justify-start">
                      <div className="rounded-2xl rounded-bl-md border border-[#e1e5dc] bg-white px-4 py-3 shadow-sm">
                        <div className="flex items-center gap-2">
                          <span className="h-2 w-2 animate-pulse rounded-full bg-[#719451]" />

                          <span className="h-2 w-2 animate-pulse rounded-full bg-[#91ad78] [animation-delay:150ms]" />

                          <span className="h-2 w-2 animate-pulse rounded-full bg-[#b3c7a1] [animation-delay:300ms]" />
                        </div>
                      </div>
                    </div>
                  )}


                  <div
                    ref={
                      messagesEndRef
                    }
                  />
                </div>
              )}
            </div>


            {error && (
              <div className="mx-5 mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 sm:mx-6">
                {error}
              </div>
            )}


            <div className="border-t border-[#e1e5dc] bg-white px-4 py-4 sm:px-6">

              {messages.length >
                0 && (
                <div className="mb-3">
                  <QuickActions
                    disabled={
                      loading
                    }
                    userRole={
                      user.role
                    }
                    onAction={(
                      message
                    ) =>
                      void sendMessage(
                        message
                      )
                    }
                  />
                </div>
              )}


              <form
                onSubmit={
                  handleSubmit
                }
                className="flex items-end gap-3 rounded-2xl border border-[#d9dfd3] bg-[#f8f9f6] p-2 shadow-inner"
              >
                <textarea
                  rows={2}
                  value={input}
                  disabled={
                    loading
                  }
                  onChange={(
                    event
                  ) =>
                    setInput(
                      event
                        .target
                        .value
                    )
                  }
                  onKeyDown={(
                    event
                  ) => {
                    if (
                      event.key ===
                        "Enter" &&
                      !event.shiftKey
                    ) {
                      event.preventDefault();

                      if (
                        input.trim() &&
                        !loading
                      ) {
                        void sendMessage(
                          input
                        );
                      }
                    }
                  }}
                  placeholder="Ask Relay anything..."
                  className="min-h-[52px] flex-1 border-0 bg-transparent px-3 py-2.5 text-sm leading-6 text-[#263022] outline-none placeholder:text-[#99a193]"
                />

                <button
                  type="submit"
                  disabled={
                    loading ||
                    !input.trim()
                  }
                  aria-label="Send message"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1d2f18] text-white transition hover:bg-[#314525] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <svg
                    viewBox="0 0 24 24"
                    className="h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path
                      d="M22 2 11 13"
                    />

                    <path
                      d="m22 2-7 20-4-9-9-4Z"
                    />
                  </svg>
                </button>
              </form>


              <p className="mt-2 text-center text-[11px] text-[#92998e]">
                Relay uses
                controlled tools,
                permissions and
                business rules for
                operational actions.
              </p>
            </div>
          </section>


          <aside className="space-y-5">

            <section className="rounded-[24px] border border-[#dce2d6] bg-white p-5 shadow-[0_12px_32px_rgba(37,53,31,0.05)]">

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8b9387]">
                    Current user
                  </p>

                  <h2 className="mt-1 text-lg font-semibold text-[#1d271a]">
                    {user.username}
                  </h2>
                </div>

                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#e4ecd9] text-sm font-semibold uppercase text-[#4f693a]">
                  {user.username
                    .slice(
                      0,
                      1
                    )}
                </div>
              </div>


              <div className="mt-5 space-y-3">

                <div className="rounded-xl bg-[#f5f7f2] p-3">
                  <p className="text-xs text-[#858d80]">
                    Role
                  </p>

                  <p className="mt-1 text-sm font-medium text-[#35422f]">
                    {roleLabel}
                  </p>
                </div>


                <div className="rounded-xl bg-[#f5f7f2] p-3">
                  <p className="text-xs text-[#858d80]">
                    Conversation
                  </p>

                  <p className="mt-1 truncate font-mono text-xs text-[#455040]">
                    {conversationId ??
                      "Not started"}
                  </p>
                </div>
              </div>
            </section>


            <section className="overflow-hidden rounded-[24px] bg-gradient-to-br from-[#8ba96f] via-[#719451] to-[#4f6e3b] p-5 text-white shadow-[0_16px_38px_rgba(68,96,48,0.20)]">

              <p className="text-xs font-medium uppercase tracking-[0.12em] text-white/70">
                Quick start
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                What would you
                like to do?
              </h2>

              <p className="mt-2 text-sm leading-6 text-white/75">
                Start one of the
                most common Relay
                workflows.
              </p>


              <div className="mt-5 space-y-2">

                {(
                  user.role ===
                    "manager" ||
                  user.role ===
                    "admin"
                ) && (
                  <button
                    type="button"
                    disabled={
                      loading
                    }
                    onClick={() =>
                      void sendMessage(
                        "Do I have any pending approvals?"
                      )
                    }
                    className="w-full rounded-xl bg-white/15 px-3 py-3 text-left text-sm font-medium backdrop-blur transition hover:bg-white/25 disabled:opacity-50"
                  >
                    Review approvals
                  </button>
                )}


                <button
                  type="button"
                  disabled={
                    loading
                  }
                  onClick={() =>
                    void sendMessage(
                      "How many Alpine Shell Jackets are available?"
                    )
                  }
                  className="w-full rounded-xl bg-white/15 px-3 py-3 text-left text-sm font-medium backdrop-blur transition hover:bg-white/25 disabled:opacity-50"
                >
                  Check inventory
                </button>


                <button
                  type="button"
                  disabled={
                    loading
                  }
                  onClick={() =>
                    void sendMessage(
                      "Quote 30 Alpine Shell Jackets for Pacific Mountain Outfitters."
                    )
                  }
                  className="w-full rounded-xl bg-white/15 px-3 py-3 text-left text-sm font-medium backdrop-blur transition hover:bg-white/25 disabled:opacity-50"
                >
                  Create a quote
                </button>
              </div>
            </section>


            <section className="rounded-[24px] border border-[#dce2d6] bg-white p-5 shadow-[0_12px_32px_rgba(37,53,31,0.05)]">

              <button
                type="button"
                onClick={() =>
                  setShowDeveloperDetails(
                    (current) =>
                      !current
                  )
                }
                className="flex w-full items-center justify-between text-left"
              >
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8b9387]">
                    Technical
                  </p>

                  <h2 className="mt-1 text-sm font-semibold text-[#273322]">
                    Developer details
                  </h2>
                </div>

                <span className="text-[#778171]">
                  {showDeveloperDetails
                    ? "−"
                    : "+"}
                </span>
              </button>


              {showDeveloperDetails && (
                <div className="mt-4 space-y-3 border-t border-[#edf0e9] pt-4">

                  <div>
                    <p className="text-xs text-[#899185]">
                      Selected agent
                    </p>

                    <p className="mt-1 font-mono text-xs text-[#40503a]">
                      {selectedAgent ??
                        "None"}
                    </p>
                  </div>


                  <div>
                    <p className="text-xs text-[#899185]">
                      Conversation ID
                    </p>

                    <p className="mt-1 break-all font-mono text-xs leading-5 text-[#40503a]">
                      {conversationId ??
                        "None"}
                    </p>
                  </div>
                </div>
              )}
            </section>

          </aside>
        </div>
      </div>
    </main>
  );
}