import {
  type FormEvent,
  useState,
} from "react";

import {
  chatWithRelay,
  type UserResponse,
} from "../api/relay";


type Message = {
  role: "user" | "assistant";
  content: string;
};


type ChatProps = {
  user: UserResponse;
};


export default function Chat(
  {
    user,
  }: ChatProps
) {
  const [
    messages,
    setMessages,
  ] = useState<Message[]>([]);

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


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    const text = input.trim();

    if (!text || loading) {
      return;
    }

    setMessages(
      (current) => [
        ...current,
        {
          role: "user",
          content: text,
        },
      ]
    );

    setInput("");
    setError(null);
    setLoading(true);

    try {
      const response =
        await chatWithRelay(
          text,
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
            role: "assistant",
            content:
              response.message,
          },
        ]
      );

    } catch (err) {
      console.error(err);

      setError(
        "The request failed. Check "
        + "the backend terminal for "
        + "details."
      );

    } finally {
      setLoading(false);
    }
  }


  function newConversation() {
    setConversationId(null);
    setSelectedAgent(null);
    setMessages([]);
    setInput("");
    setError(null);
  }


  return (
    <div>
      <h1>Relay AI</h1>

      <p>
        Logged in as:{" "}
        <strong>
          {user.username}
        </strong>
      </p>

      <p>
        Role:{" "}
        <strong>
          {user.role}
        </strong>
      </p>

      <button
        onClick={
          newConversation
        }
      >
        New Conversation
      </button>

      <p>
        Conversation ID:{" "}
        {conversationId ?? "None"}
      </p>

      <p>
        Internal agent:{" "}
        {selectedAgent ?? "None"}
      </p>

      <hr />

      <div>
        {messages.length === 0 && (
          <p>
            Start a conversation
            with Relay.
          </p>
        )}

        {messages.map(
          (
            message,
            index
          ) => (
            <div key={index}>
              <p>
                <strong>
                  {message.role
                    === "user"
                    ? "You"
                    : "Relay"}
                  :
                </strong>
              </p>

              <p
                style={{
                  whiteSpace:
                    "pre-wrap",
                }}
              >
                {message.content}
              </p>
            </div>
          )
        )}
      </div>

      {loading && (
        <p>
          Relay is working...
        </p>
      )}

      {error && (
        <p>
          {error}
        </p>
      )}

      <hr />

      <form
        onSubmit={
          handleSubmit
        }
      >
        <textarea
          rows={4}
          cols={70}
          value={input}
          onChange={
            (event) =>
              setInput(
                event.target.value
              )
          }
          placeholder={
            "Ask Relay something..."
          }
        />

        <br />

        <button
          type="submit"
          disabled={loading}
        >
          Send
        </button>
      </form>
    </div>
  );
}