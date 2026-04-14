# Agent Framework (LangGraph)

> Build the 4-node LangGraph state graph that powers the QBR generation pipeline: Quant Agent, Qual Agent, Strategist, and Editor.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `NOT_STARTED`                  |
| Owner         | —                              |
| Last Updated  | —                              |

### Dependencies

| Work State File            | Required Status |
|----------------------------|-----------------|
| `00_infrastructure.md`     | `DONE`          |
| `01_data_layer.md`         | `DONE`          |

---

## Objective

Implement a deterministic, inspectable LangGraph workflow that takes a customer account as input and produces a complete Markdown QBR draft. The graph separates concerns into four specialized nodes to avoid monolithic prompts, reduce hallucinations, and enable structured intermediate outputs. Each node's output must be independently inspectable for debugging and trust.

---

## Plan

- [ ] Define the `WorkflowState` TypedDict in `backend/app/agents/state.py`:
  ```python
  class WorkflowState(TypedDict):
      account: CustomerAccount        # input
      quantitative_insights: dict     # output of Quant Agent
      qualitative_insights: dict      # output of Qual Agent
      strategic_synthesis: dict       # output of Strategist
      final_draft: str                # output of Editor (Markdown)
  ```
  Note: No `thought_log` field needed — AG-UI protocol handles lifecycle event streaming (`STEP_STARTED`/`STEP_FINISHED`) automatically via the `ag-ui-langgraph` adapter.
- [ ] Define Pydantic output schemas in `backend/app/agents/schemas.py`:
  - `QuantInsights`: `health_status`, `key_metrics`, `growth_trend`, `risk_flags`
  - `QualInsights`: `overall_sentiment`, `core_themes`, `key_quotes`, `action_signals`
  - `StrategicSynthesis`: `executive_summary`, `strengths`, `concerns`, `recommendations` (list of `{recommendation: str, evidence: str, grounding_metrics: list[str]}`), `cross_sell_opportunities`, `data_citations` (list of strings linking insights back to source fields)
- [ ] Implement **Node 1: Quant Agent** in `backend/app/agents/quant_agent.py`:
  - Input: structured numeric fields from `CustomerAccount` (active_users, usage_growth_qoq, automation_adoption_pct, tickets_last_quarter, avg_response_time, nps_score, scat_score, risk_engine_score)
  - Prompt: analyze metrics, classify health, identify trends
  - Output: `QuantInsights` (structured JSON via OpenAI function calling)
- [ ] Implement **Node 2: Qual Agent** in `backend/app/agents/qual_agent.py`:
  - Input: unstructured text fields (crm_notes, feedback_summary)
  - Prompt: extract sentiment, themes, actionable signals
  - Output: `QualInsights` (structured JSON)
- [ ] Implement **Node 3: Strategist** in `backend/app/agents/strategist.py`:
  - Input: `QuantInsights` + `QualInsights` + `preferred_channel` (main communication preference — Email / Phone / Chat / In-app chat) from the original account
  - Prompt: synthesize quantitative and qualitative findings, find intersections, generate evidence-grounded recommendations that cite specific metrics, factor in preferred communication channel for engagement recommendations
  - Output: `StrategicSynthesis` (structured JSON) — each recommendation includes an `evidence` field and `grounding_metrics` list
- [ ] Implement **Node 4: Editor** in `backend/app/agents/editor.py`:
  - Input: `StrategicSynthesis` + original `CustomerAccount` for context
  - Prompt: format into a crisp, slide-ready Markdown QBR narrative with sections (Executive Summary, Key Metrics, Health Assessment, Recommendations, Next Steps)
  - Output: `final_draft` (Markdown string)
- [ ] Wire the LangGraph `StateGraph` in `backend/app/agents/graph.py`:
  - Add all 4 nodes
  - Define edges: `START -> quant_agent -> qual_agent -> strategist -> editor -> END`
  - Note: Quant and Qual could run in parallel (future optimization), but sequential is simpler for the PoC
  - AG-UI adapter emits `STEP_STARTED`/`STEP_FINISHED` events automatically as each LangGraph node executes — no manual thought-log management needed
- [ ] Wrap the compiled graph with `ag-ui-langgraph` for AG-UI event emission (used by the API layer to stream to the frontend)
- [ ] Implement `run_qbr_pipeline(account: CustomerAccount) -> WorkflowState` entry point in `graph.py`
- [ ] Implement `refine_draft(current_draft: str, instructions: str) -> str` standalone function in `backend/app/agents/refiner.py` for the HITL refinement endpoint
- [ ] Manual integration test: run the full pipeline for "Altura Systems" and verify the output Markdown is coherent and all intermediate states are populated

---

## Acceptance Criteria

- [ ] `from app.agents.graph import run_qbr_pipeline` is importable
- [ ] Running `run_qbr_pipeline(altura_account)` returns a `WorkflowState` where:
  - `quantitative_insights` is a valid `QuantInsights` dict
  - `qualitative_insights` is a valid `QualInsights` dict
  - `strategic_synthesis` is a valid `StrategicSynthesis` dict
  - `final_draft` is a non-empty Markdown string with recognizable QBR sections
- [ ] Running the graph via the AG-UI adapter emits `STEP_STARTED` and `STEP_FINISHED` events for each of the 4 nodes
- [ ] Each recommendation in `StrategicSynthesis` includes an `evidence` field citing specific metrics
- [ ] Running `refine_draft(draft, "Make the tone more optimistic")` returns a modified Markdown string
- [ ] All structured outputs conform to their Pydantic schemas (no extra/missing fields)
- [ ] Each node can be tested independently by constructing a partial `WorkflowState`

---

## Technical Decisions

_No decisions yet._

---

## Dependencies Detail

### `00_infrastructure.md`

- **What is needed:** Python environment with `langgraph`, `langchain`, `langchain-openai`, `pydantic`, `ag-ui-protocol`, and `ag-ui-langgraph` installed. A valid `OPENAI_API_KEY` in `.env`.
- **Expected interface/contract:** `uv run python -c "import langgraph; import langchain_openai; from ag_ui_langgraph import add_langgraph_fastapi_endpoint; print('ok')"` succeeds inside `backend/`.

### `01_data_layer.md`

- **What is needed:** The `CustomerAccount` Pydantic model and the data loader.
- **Expected interface/contract:** `from app.models.customer import CustomerAccount` and `from app.data.loader import get_account_by_name` work correctly. A `CustomerAccount` object has all 13 typed fields.

---

## Log

_No entries yet._
