# Relay AI

Relay AI is an enterprise AI workflow and agent orchestration platform designed to simulate how organizations can safely integrate large language models into real business processes.

The platform connects AI-assisted workflows with simulated enterprise systems such as CRM, inventory, pricing, and order management. Rather than allowing an LLM to freely generate business decisions, Relay AI separates AI reasoning from authoritative business logic, permissions, approvals, and system actions.

## What Relay AI Does

Relay AI allows users to submit natural-language business requests and converts them into structured, auditable workflows.

For example, a salesperson could ask:

> "Pacific Industrial needs 120 cases of 5W-30 synthetic oil. Can we fulfill the order and what price should they receive?"

Relay AI is designed to:

- interpret the user's request
- identify the customer and requested products
- retrieve customer information from the CRM system
- check inventory across warehouses
- retrieve approved customer-specific pricing
- determine whether the request can be fulfilled
- generate a business recommendation or draft response
- determine whether human approval is required
- execute approved actions through controlled tools
- record the full workflow for monitoring and auditing

The LLM is never treated as the source of truth for inventory, pricing, customer data, permissions, or other authoritative business information. Those values are retrieved from deterministic business systems.

## Core Design Principle

Relay AI follows a layered decision model:

```text
AI interprets and reasons
        ↓
Business logic validates
        ↓
Permissions authorize
        ↓
APIs perform actions
        ↓
Humans approve sensitive actions
        ↓
Monitoring records everything
```

This design allows AI to handle flexible reasoning and natural-language interpretation while keeping business-critical operations controlled, validated, and auditable.

## Business Systems

Relay AI simulates several internal enterprise systems that serve as the source of truth for AI workflows.

### CRM

The CRM system manages customer and account information such as:

- customer identifiers
- customer names
- regions
- pricing tiers
- credit status
- account activity

### Inventory and ERP

The inventory and ERP system manages:

- product SKUs
- warehouse locations
- available inventory
- reserved inventory
- orders
- fulfillment information

### Pricing

The pricing system manages:

- product pricing
- customer pricing tiers
- approved unit prices
- discount rules
- customer-specific pricing logic

These systems provide the authoritative business data used throughout AI-assisted workflows.

## AI Workflow Orchestration

Relay AI uses LangGraph to coordinate stateful, multi-step workflows.

A typical quote workflow may look like:

```text
User Request
      ↓
Parse Request
      ↓
Identify Customer
      ↓
Identify Product
      ↓
Check Inventory
      ↓
Retrieve Pricing
      ↓
Evaluate Request
      ↓
Generate Recommendation
      ↓
Approval Required?
   ↙             ↘
 Yes             No
 ↓                ↓
Human Approval   Continue
      ↓
Execute Action
      ↓
Audit + Monitoring
```

Each workflow step is designed to be inspectable and traceable.

The system can preserve workflow state, handle branching logic, pause for approvals, and recover from failures.

## AI Agents

Relay AI will support specialized agents responsible for different areas of the business.

### Sales Agent

The Sales Agent is responsible for:

- customer lookups
- quote requests
- product inquiries
- sales-related recommendations

### Inventory Agent

The Inventory Agent is responsible for:

- stock checks
- low-stock analysis
- warehouse availability
- inventory transfer recommendations

### Finance Agent

The Finance Agent is responsible for:

- invoice questions
- customer credit-status lookups
- payment summaries
- finance-related recommendations

Agents can eventually hand work off to one another while maintaining workflow state, permissions, and audit history.

## Controlled Tool Use

AI agents do not directly access the database.

Instead, agents interact with approved tools that communicate with internal services and APIs.

```text
LLM
 ↓
Agent
 ↓
Approved Tool
 ↓
Internal API
 ↓
Database
```

Examples of approved tools include:

- customer lookup
- product lookup
- inventory lookup
- pricing lookup
- order creation
- CRM activity creation

This allows Relay AI to control exactly what actions an AI agent can perform.

## Human-in-the-Loop Controls

Sensitive or restricted actions require human approval before execution.

Examples include:

- creating orders
- approving quotes
- changing pricing
- performing restricted write operations
- recommending inventory transfers
- executing actions above a user's authority level

Users and agents have defined permissions, so AI actions are constrained by the authority of the current business role.

A workflow can pause while waiting for approval and resume after the decision is made.

## Authentication and Permissions

Relay AI includes role-based access control.

Planned roles include:

- Sales Representative
- Sales Manager
- Supply Chain Manager
- Finance
- Administrator

Each role has specific permissions.

For example:

```text
Sales Representative
- read customers
- read inventory
- read pricing
- create quote drafts

Sales Manager
- read customers
- read inventory
- read pricing
- create quotes
- approve quotes

Supply Chain Manager
- read inventory
- recommend inventory transfers
```

If an AI agent attempts an action that exceeds the current user's authority, the system can reject the action or create an approval request.

## Reliability and Failure Handling

Relay AI is designed around the assumption that AI models, APIs, and external systems can fail.

The platform includes or will include:

- structured LLM output validation
- retries
- exponential backoff
- API timeouts
- exception handling
- idempotency
- workflow recovery paths
- audit trails
- malformed response handling
- database failure handling
- model failure handling
- human escalation paths

The goal is to make AI workflows behave more like reliable production systems rather than simple chatbot interactions.

## Idempotency

Relay AI protects important write operations from being executed more than once.

For example, if an order is created successfully but the response is lost because of a timeout, a retry should not create a duplicate order.

The system can use idempotency keys such as:

```text
WF-83928-CREATE-ORDER
```

Before executing an operation, Relay AI checks whether the same action has already been completed.

## AgentOps and Monitoring

Relay AI will include an AgentOps dashboard for monitoring AI workflow performance and system reliability.

Planned metrics include:

- workflow success rate
- failed workflows
- workflows awaiting approval
- average workflow latency
- model latency
- API latency
- AI usage
- model cost
- tool-call success rate
- workflow execution history
- audit events
- exceptions

Individual workflow runs will also include step-by-step traces.

Example:

```text
12:41:03 request_received
12:41:03 llm_parse_start
12:41:04 llm_parse_success
12:41:04 customer_lookup
12:41:05 inventory_lookup
12:41:07 timeout
12:41:08 retry
12:41:08 inventory_success
12:41:09 pricing_success
12:41:10 response_generated
12:41:10 approval_requested
```

This makes it possible to understand exactly what happened during an AI-assisted business process.

## AI Evaluation

Relay AI will include an evaluation framework for measuring AI performance rather than assuming model responses are correct.

Models can be evaluated on:

- intent classification accuracy
- entity extraction accuracy
- structured-output reliability
- tool selection accuracy
- invalid action rate
- latency
- token usage
- estimated cost

The platform will initially use AWS Bedrock and may later support additional providers such as OpenAI and Anthropic.

## Multi-Model Support

Relay AI is designed to avoid tightly coupling business workflows to a single LLM provider.

A provider abstraction will allow different models to be used without rewriting the underlying workflow logic.

Planned providers include:

```text
AWS Bedrock
OpenAI
Anthropic
```

This also allows models to be compared based on task performance, reliability, latency, and cost.

## Architecture

```text
                    React Frontend
                          │
                          ▼
                      FastAPI
                          │
              Authentication / RBAC
                          │
                          ▼
                     LangGraph
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   CRM Tools        Inventory Tools    Pricing Tools
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                     PostgreSQL
                          │
                          ▼
                     AWS Bedrock
                          │
                          ▼
                  Pydantic Validation
                          │
                          ▼
                 Approval / Execution
                          │
                          ▼
                Audit + Monitoring
```

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- REST APIs
- httpx

### AI

- LangGraph
- AWS Bedrock
- additional LLM providers planned

### Data

- PostgreSQL
- Alembic

### Background Processing

- Celery
- Redis

### Testing

- pytest

### Infrastructure

- Docker
- Docker Compose
- AWS
- GitHub Actions

## Project Goals

Relay AI is designed to demonstrate how AI can be integrated into business systems in a way that is:

- useful
- controlled
- auditable
- reliable
- explainable
- secure
- measurable
- production-oriented

The project focuses on the engineering required to move beyond an AI prototype and toward dependable AI-enabled business workflows.
