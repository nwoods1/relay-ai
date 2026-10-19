type ChatMessageProps = {
  role: "user" | "assistant";
  content: string;
};


export default function ChatMessage({
  role,
  content,
}: ChatMessageProps) {
  const isUser =
    role === "user";

  return (
    <div
      className={`flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`max-w-[82%] ${
          isUser
            ? "items-end"
            : "items-start"
        }`}
      >
        <div
          className={`mb-1 flex items-center gap-2 ${
            isUser
              ? "justify-end"
              : "justify-start"
          }`}
        >
          {!isUser && (
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#719451] text-xs font-semibold text-white">
              R
            </div>
          )}

          <span className="text-xs font-medium text-[#727a6e]">
            {isUser
              ? "You"
              : "Relay"}
          </span>
        </div>

        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
            isUser
              ? "rounded-br-md bg-[#1d2f18] text-white"
              : "rounded-bl-md border border-[#e1e5dc] bg-white text-[#263022]"
          }`}
        >
          <p className="whitespace-pre-wrap">
            {content}
          </p>
        </div>
      </div>
    </div>
  );
}