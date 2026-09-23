import { useState } from "react";

import {
  clearAccessToken,
  setAccessToken,
} from "../api/client";

import {
  createQuote,
  decideApproval,
  getAgentOpsSummary,
  getMe,
  getPendingApprovals,
  getWorkflowRun,
  getWorkflowRuns,
  login,
} from "../api/relay";


function generateKey(): string {
  return crypto.randomUUID();
}


export default function SystemTest() {
  const [username, setUsername] =
    useState<string>("sales");

  const [password, setPassword] =
    useState<string>("Sales123!");

  const [message, setMessage] =
    useState<string>(
      "Pacific Mountain Outfitters wants 1 Merino Wool Toque."
    );

  const [
    idempotencyKey,
    setIdempotencyKey,
  ] = useState<string>(
    generateKey()
  );

  const [threadId, setThreadId] =
    useState<string>("");

  const [output, setOutput] =
    useState<unknown>(null);

  const [loading, setLoading] =
    useState<boolean>(false);


  async function run(
    action: () => Promise<unknown>
  ) {
    try {
      setLoading(true);

      const result =
        await action();

      setOutput(result);

      if (
        typeof result === "object"
        && result !== null
        && "thread_id" in result
      ) {
        setThreadId(
          String(
            (
              result as {
                thread_id: unknown;
              }
            ).thread_id
          )
        );
      }
    } catch (error) {
      setOutput(error);
    } finally {
      setLoading(false);
    }
  }


  async function handleLogin() {
    await run(
      async () => {
        const result = await login(
          username,
          password
        );

        setAccessToken(
          result.access_token
        );

        return result;
      }
    );
  }


  return (
    <div>
      <h1>Relay AI System Test</h1>

      <p>
        Use this page to test the backend
        without Postman.
      </p>

      <hr />

      <h2>1. Authentication</h2>

      <button
        onClick={() => {
          setUsername("sales");
          setPassword("Sales123!");
        }}
      >
        Sales
      </button>

      <button
        onClick={() => {
          setUsername("manager");
          setPassword("Manager123!");
        }}
      >
        Manager
      </button>

      <button
        onClick={() => {
          setUsername("admin");
          setPassword("Admin123!");
        }}
      >
        Admin
      </button>

      <br />
      <br />

      <label>
        Username:
      </label>

      <br />

      <input
        value={username}
        onChange={(event) =>
          setUsername(
            event.target.value
          )
        }
      />

      <br />
      <br />

      <label>
        Password:
      </label>

      <br />

      <input
        type="password"
        value={password}
        onChange={(event) =>
          setPassword(
            event.target.value
          )
        }
      />

      <br />
      <br />

      <button
        onClick={handleLogin}
      >
        Login
      </button>

      <button
        onClick={() =>
          run(getMe)
        }
      >
        Get Current User
      </button>

      <button
        onClick={() => {
          clearAccessToken();

          setOutput({
            message: "Logged out",
          });
        }}
      >
        Logout
      </button>

      <hr />

      <h2>
        2. AI Quote Workflow
      </h2>

      <label>
        Quote request:
      </label>

      <br />

      <textarea
        rows={5}
        cols={70}
        value={message}
        onChange={(event) =>
          setMessage(
            event.target.value
          )
        }
      />

      <br />
      <br />

      <label>
        Idempotency Key:
      </label>

      <br />

      <input
        size={50}
        value={idempotencyKey}
        onChange={(event) =>
          setIdempotencyKey(
            event.target.value
          )
        }
      />

      <button
        onClick={() =>
          setIdempotencyKey(
            generateKey()
          )
        }
      >
        Generate New Key
      </button>

      <br />
      <br />

      <button
        onClick={() =>
          run(
            () =>
              createQuote(
                message,
                idempotencyKey
              )
          )
        }
      >
        Create Quote
      </button>

      <button
        onClick={() => {
          setMessage(
            "Pacific Mountain Outfitters wants 1 Merino Wool Toque."
          );

          setIdempotencyKey(
            generateKey()
          );
        }}
      >
        Load Normal Quote
      </button>

      <button
        onClick={() => {
          setMessage(
            "Pacific Mountain Outfitters wants 500 Alpine Shell Jackets."
          );

          setIdempotencyKey(
            generateKey()
          );
        }}
      >
        Load Approval Quote
      </button>

      <hr />

      <h2>
        3. Human Approval
      </h2>

      <label>
        Thread ID:
      </label>

      <br />

      <input
        size={50}
        value={threadId}
        onChange={(event) =>
          setThreadId(
            event.target.value
          )
        }
      />

      <br />
      <br />

      <button
        onClick={() =>
          run(
            getPendingApprovals
          )
        }
      >
        Get Pending Approvals
      </button>

      <button
        onClick={() =>
          run(
            () =>
              decideApproval(
                threadId,
                "approved",
                "Approved from frontend.",
                generateKey()
              )
          )
        }
      >
        Approve
      </button>

      <button
        onClick={() =>
          run(
            () =>
              decideApproval(
                threadId,
                "rejected",
                "Rejected from frontend.",
                generateKey()
              )
          )
        }
      >
        Reject
      </button>

      <hr />

      <h2>
        4. AgentOps
      </h2>

      <button
        onClick={() =>
          run(
            getAgentOpsSummary
          )
        }
      >
        Get Summary
      </button>

      <button
        onClick={() =>
          run(
            getWorkflowRuns
          )
        }
      >
        Get Workflow Runs
      </button>

      <button
        onClick={() =>
          run(
            () =>
              getWorkflowRun(
                threadId
              )
          )
        }
      >
        Inspect Thread
      </button>

      <hr />

      <h2>
        API Response
      </h2>

      {loading && (
        <p>Loading...</p>
      )}

      <pre>
        {JSON.stringify(
          output,
          null,
          2
        )}
      </pre>
    </div>
  );
}