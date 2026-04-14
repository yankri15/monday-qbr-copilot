# Backend API (FastAPI)

> Expose the data layer and agent framework as HTTP endpoints with SSE streaming for the frontend.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | Agent                          |
| Last Updated  | 2026-04-14                     |

### Dependencies

| Work State File            | Required Status  |
|----------------------------|------------------|
| `01_data_layer.md`         | `DONE`           |
| `02_agent_framework.md`    | `DONE`           |

---

## Objective

Build a FastAPI application that serves as the bridge between the React frontend and the AI pipeline. It must expose three endpoints: one for listing accounts, one for generating a QBR with real-time AG-UI protocol streaming of the agent's thought process, and one for refining a draft via natural language instructions. CORS must be configured so the Next.js dev server can call the API. The generate endpoint uses the AG-UI protocol (`ag-ui-langgraph`) for standardized SSE event streaming.

---

## Plan

- [x] Create the FastAPI app entrypoint at `backend/app/main.py`:
  - Initialize the FastAPI app instance
  - Configure CORS middleware (allow `http://localhost:3000` and the future Vercel domain)
  - Mount the API router
- [x] Implement `GET /api/accounts` in `backend/app/routes/accounts.py`:
  - Call `get_all_accounts()` from the data loader
  - Return serialized list of `CustomerAccount` objects as JSON
  - Response model: `list[CustomerAccountResponse]` (a Pydantic model mirroring `CustomerAccount` for the API contract)
- [x] Implement `POST /api/generate-qbr` in `backend/app/routes/qbr.py`:
  - Request body: `{ "account_name": str }` (thin wrapper; internally maps to AG-UI `RunAgentInput`)
  - Look up the account via `get_account_by_name()`
  - Return 404 if not found
  - Execute the LangGraph pipeline via the AG-UI adapter, streaming standardized SSE events
  - AG-UI SSE event flow:
    ```
    event: RUN_STARTED
    data: {"threadId": "...", "runId": "..."}

    event: STEP_STARTED
    data: {"stepName": "quant_agent", "message": "Analyzing usage metrics..."}

    event: STATE_DELTA
    data: {"quantitative_insights": {...}}

    event: STEP_FINISHED

    event: STEP_STARTED
    data: {"stepName": "qual_agent", "message": "Extracting sentiment from CRM notes..."}

    event: STATE_DELTA
    data: {"qualitative_insights": {...}}

    event: STEP_FINISHED

    ... (strategist, editor follow same pattern) ...

    event: TEXT_MESSAGE_CONTENT
    data: {"content": "<final markdown draft>"}

    event: RUN_FINISHED
    ```
  - Use `ag-ui-langgraph` `add_langgraph_fastapi_endpoint()` or manual `EventEncoder` from `ag_ui.encoder` for streaming
- [x] Implement `POST /api/refine-qbr` in `backend/app/routes/qbr.py`:
  - Request body: `{ "current_draft": str, "instructions": str }`
  - Call `refine_draft()` from the agent framework
  - Return `{ "refined_draft": str }`
- [x] Define request/response Pydantic models in `backend/app/models/api.py`:
  - `GenerateQBRRequest(account_name: str)`
  - `RefineQBRRequest(current_draft: str, instructions: str)`
  - `RefineQBRResponse(refined_draft: str)`
- [x] Add error handling middleware:
  - 404 for unknown accounts
  - 500 with safe error messages for LLM failures
  - Request validation errors (422) handled by FastAPI automatically
- [x] Add a health check endpoint: `GET /api/health` returning `{ "status": "ok" }`
- [x] Verify all endpoints via `curl` commands:
  - `curl http://localhost:8000/api/accounts`
  - `curl -X POST http://localhost:8000/api/generate-qbr -H "Content-Type: application/json" -d '{"account_name": "Altura Systems"}'`
  - `curl -X POST http://localhost:8000/api/refine-qbr -H "Content-Type: application/json" -d '{"current_draft": "...", "instructions": "Make it shorter"}'`

---

## Acceptance Criteria

- [x] `GET /api/health` returns `{"status": "ok"}` with status 200
- [x] `GET /api/accounts` returns a JSON array of 5 account objects, each with all 13 fields
- [x] `POST /api/generate-qbr` with `{"account_name": "Altura Systems"}` streams AG-UI SSE events (`RUN_STARTED`, `STEP_STARTED`/`STEP_FINISHED` for each node, `STATE_DELTA` with intermediate insights, `TEXT_MESSAGE_CONTENT` with the final draft, `RUN_FINISHED`)
- [x] `POST /api/generate-qbr` with an unknown account returns 404
- [x] `POST /api/refine-qbr` with a draft and instructions returns a modified draft
- [x] CORS headers allow requests from `http://localhost:3000`
- [x] The API server starts via `uv run uvicorn app.main:app --reload` from the `backend/` directory

---

## Technical Decisions

- The API uses a custom SSE adapter around `LangGraphAgent.run(...)` instead of `add_langgraph_fastapi_endpoint()` directly so the route can accept a simple `{ "account_name": str }` payload and emit a cleaner stream tailored to the frontend contract.
- `STATE_DELTA` events are derived from successive `STATE_SNAPSHOT` payloads emitted by `ag-ui-langgraph`, limited to `quantitative_insights`, `qualitative_insights`, and `strategic_synthesis`.
- Intermediate model token streams are intentionally filtered out of `/api/generate-qbr`; only lifecycle events, derived state deltas, and the final draft text message are exposed.
- CORS explicitly allows local Next.js development origins (`http://localhost:3000`, `http://127.0.0.1:3000`) plus Vercel preview domains via regex.
- Unhandled non-HTTP exceptions return a safe `500` JSON response with `{"detail": "Internal server error"}`.

---

## Dependencies Detail

### `01_data_layer.md`

- **What is needed:** The `CustomerAccount` model and the data loader functions (`get_all_accounts`, `get_account_by_name`).
- **Expected interface/contract:**
  - `get_all_accounts() -> list[CustomerAccount]` returns 5 objects
  - `get_account_by_name(name: str) -> CustomerAccount | None` returns an account or None
  - `CustomerAccount` is a Pydantic model serializable to JSON via `.model_dump()`

### `02_agent_framework.md`

- **What is needed:** The compiled LangGraph graph (wrapped with `ag-ui-langgraph` adapter) and the refiner function.
- **Expected interface/contract:**
  - The compiled graph is exposed as an AG-UI-compatible agent via `add_langgraph_fastapi_endpoint()` or manually invoked with `EventEncoder` to emit AG-UI events
  - AG-UI lifecycle events (`STEP_STARTED`/`STEP_FINISHED`) are emitted automatically as each node runs
  - `STATE_DELTA` events stream intermediate insights (`quantitative_insights`, `qualitative_insights`, `strategic_synthesis`) to the frontend in real time
  - `WorkflowState["final_draft"]` is the Markdown string delivered via `TEXT_MESSAGE_CONTENT` event
  - `refine_draft(current_draft: str, instructions: str) -> str` returns a refined Markdown string (no streaming needed)

---

## Log

- **2026-04-14** — Added FastAPI app entrypoint, API request/response models, and `/api/health`, `/api/accounts`, `/api/generate-qbr`, `/api/refine-qbr` routes.
- **2026-04-14** — Implemented a custom AG-UI SSE adapter that transforms LangGraph state snapshots into `STATE_DELTA` events and emits the final markdown draft as `TEXT_MESSAGE_*` events.
- **2026-04-14** — Added `backend/tests/test_backend_api.py` covering health, accounts, CORS, unknown-account handling, refinement, and mocked streaming behavior.
- **2026-04-14** — Verified `uv run python -m unittest discover -s tests -v` passes locally across data layer, agent framework, and backend API tests.
- **2026-04-14** — Verified `GET /api/health` and `GET /api/accounts` through the FastAPI HTTP surface, and live OpenAI-backed HTTP checks confirmed `/api/generate-qbr` streams `RUN_STARTED`, `STEP_STARTED`, `STATE_DELTA`, `TEXT_MESSAGE_CONTENT`, and `RUN_FINISHED`, while `/api/refine-qbr` returned a shortened draft.
