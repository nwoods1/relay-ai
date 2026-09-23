import {
  apiRequest,
} from "./client";



export interface LoginResponse {
  access_token: string;
  token_type: string;
}


export interface UserResponse {
  id: number;
  username: string;
  role: string;
}


export interface WorkflowError {
  type: string;
  message: string;
  failed_node: string | null;
  retry_count: number | null;
}


export interface QuoteWorkflowResponse {
  thread_id: string;
  status: string;
  quote: Record<string, unknown> | null;
  approval_request:
    Record<string, unknown> | null;
  error: WorkflowError | null;
}


export interface PendingApproval {
  thread_id: string;
  status: string;
  requested_by_user_id: number;
  created_at: string;
}


export interface ApprovalResponse {
  thread_id: string;
  status: string;
  quote: Record<string, unknown> | null;
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
  metadata?: Record<
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

export interface AgentAction {
  type: string;
  data:
    | Record<string, unknown>
    | null;
}


export interface AgentChatResponse {
  conversation_id: string;
  message: string;

  action: AgentAction | null;

  workflow_thread_id:
    | string
    | null;

  awaiting_confirmation: boolean;
  selected_agent: string | null;
}


export interface AgentConversationMessage {
  role: string;
  content: string;
  message_type: string;

  workflow_thread_id:
    | string
    | null;

  created_at: string;
}


export interface ConversationHistory {
  conversation_id: string;
  messages:
    AgentConversationMessage[];
}


export function login(
  username: string,
  password: string
) {
  return apiRequest<LoginResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    }
  );
}


export function getMe() {
  return apiRequest<UserResponse>(
    "/auth/me"
  );
}


export function createQuote(
  message: string,
  idempotencyKey: string
) {
  return apiRequest<QuoteWorkflowResponse>(
    "/ai/quote",
    {
      method: "POST",
      headers: {
        "Idempotency-Key":
          idempotencyKey,
      },
      body: JSON.stringify({
        message,
      }),
    }
  );
}


export function getPendingApprovals() {
  return apiRequest<
    PendingApproval[]
  >(
    "/approvals/"
  );
}


export function decideApproval(
  threadId: string,
  decision: "approved" | "rejected",
  comment: string,
  idempotencyKey: string
) {
  return apiRequest<ApprovalResponse>(
    `/approvals/${threadId}`,
    {
      method: "POST",
      headers: {
        "Idempotency-Key":
          idempotencyKey,
      },
      body: JSON.stringify({
        decision,
        comment,
      }),
    }
  );
}


export function getWorkflowRuns() {
  return apiRequest<
    WorkflowRunSummary[]
  >(
    "/agentops/runs"
  );
}


export function getWorkflowRun(
  threadId: string
) {
  return apiRequest<
    WorkflowRunDetail
  >(
    `/agentops/runs/${threadId}`
  );
}


export function getAgentOpsSummary() {
  return apiRequest<
    AgentOpsSummary
  >(
    "/agentops/summary"
  );
}


export function chatWithRelay(
  message: string,
  conversationId:
    string | null,
  idempotencyKey: string
) {
  return apiRequest<
    AgentChatResponse
  >(
    "/agent/chat",
    {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id:
          conversationId,
        idempotency_key:
          idempotencyKey,
      }),
    }
  );
}


export function getConversation(
  conversationId: string
) {
  return apiRequest<
    ConversationHistory
  >(
    `/agent/conversations/${conversationId}`
  );
}