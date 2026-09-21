export interface AgentOpsSummary {
  total_runs: number;
  ready_runs: number;
  awaiting_approval_runs: number;
  approved_runs: number;
  rejected_runs: number;
  failed_runs: number;
  average_duration_ms: number | null;
  total_tokens: number;
}


export interface WorkflowRunSummary {
  thread_id: string;
  operation: string;
  username: string;
  user_role: string;
  status: string;
  current_node: string | null;
  requires_approval: boolean;
  total_tokens: number;
  duration_ms: number | null;
  started_at: string;
  completed_at: string | null;
}


export interface WorkflowEvent {
  id: number;
  event_type: string;
  node_name: string | null;
  status: string;
  message: string | null;
  metadata: Record<
    string,
    unknown
  > | null;
  created_at: string;
}


export interface WorkflowRunDetail
  extends WorkflowRunSummary {
  error_type: string | null;
  error_message: string | null;
  retry_count: number;
  input_tokens: number;
  output_tokens: number;
  llm_latency_ms: number | null;
  events: WorkflowEvent[];
}


const API_URL =
  "http://127.0.0.1:8000/api";


function getAuthHeaders() {
  const token =
    localStorage.getItem(
      "access_token"
    );

  return {
    Authorization:
      `Bearer ${token}`,
  };
}


export async function
getAgentOpsSummary():
  Promise<AgentOpsSummary> {

  const response = await fetch(
    `${API_URL}/agentops/summary`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load AgentOps summary"
    );
  }

  return response.json();
}


export async function
getWorkflowRuns():
  Promise<WorkflowRunSummary[]> {

  const response = await fetch(
    `${API_URL}/agentops/runs`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load workflow runs"
    );
  }

  return response.json();
}


export async function
getWorkflowRun(
  threadId: string
): Promise<WorkflowRunDetail> {

  const response = await fetch(
    `${API_URL}/agentops/runs/${threadId}`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load workflow run"
    );
  }

  return response.json();
}