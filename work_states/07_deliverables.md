# Final Deliverables (Flow Diagram + Experiment & Reflection)

> Produce the remaining assignment deliverables: Flow Architecture Diagram and Experiment & Reflection write-up.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `NOT_STARTED`                  |
| Owner         | —                              |
| Last Updated  | —                              |

### Dependencies

| Work State File            | Required Status | Notes                                                 |
|----------------------------|-----------------|-------------------------------------------------------|
| `02_agent_framework.md`    | `DONE`          | Need finalized LangGraph graph to export diagram      |
| `03_backend_api.md`        | `DONE`          | Need working API for full system diagram              |
| `04_frontend.md`           | `DONE`          | Need working UI to reflect on full e2e experience     |
| `06_documentation.md`      | `DONE`          | Design Brief and Prompts docs should be done first    |

**Note:** This workstream is explicitly blocked until the PoC is complete and working smoothly. Only then do we move on to produce these deliverables.

---

## Objective

Create the final two assignment deliverables: a visual flow architecture diagram showing the complete data-to-output pipeline, and a one-page experiment & reflection document covering what worked, what didn't, and what's next. Both are produced after the PoC is validated end-to-end.

---

## Plan

### Deliverable 2: Flow Architecture Diagram

Per the assignment: *"Visual or schematic showing how data flows from source -> processing -> AI reasoning -> output. You can use draw.io, Miro, markdown ASCII, or a simple table."*

- [ ] Generate the LangGraph state graph programmatically:
  - Use `graph.get_graph().draw_mermaid()` to export the node/edge structure as Mermaid syntax
  - This gives the exact runtime graph, not a hand-drawn approximation
- [ ] Extend the diagram to show the full system architecture (not just the agent graph):
  - Data source: `sample_customers_q3_2025.xlsx` -> Pydantic `CustomerAccount` models
  - API layer: FastAPI endpoints (`/accounts`, `/generate-qbr`, `/refine-qbr`)
  - Agent pipeline: Quant Agent -> Qual Agent -> Strategist -> Editor (with structured I/O schemas)
  - Streaming layer: AG-UI protocol events (`STEP_STARTED`, `STATE_DELTA`, `TEXT_MESSAGE_CONTENT`)
  - Frontend: Next.js + CopilotKit consuming AG-UI events
  - HITL loop: Editor view -> Refine chat -> `/refine-qbr` -> updated draft
- [ ] Create the diagram in at least two formats:
  - Mermaid (embeddable in Markdown, renders in GitHub)
  - PNG/SVG export (for presentation slides)
- [ ] Save as `docs/flow_architecture_diagram.md` (Mermaid) and `docs/flow_architecture_diagram.png` (export)

### Deliverable 6: Experiment & Reflection (1 page)

Per the assignment: *"One-pager explaining how you'd measure or improve this solution. What worked? What didn't? What's next (e.g., adding visuals, connecting to monday boards)?"*

- [ ] Write the **What Worked** section:
  - Separation of concerns via LangGraph nodes reduced hallucinations
  - Pydantic structured outputs enforced type safety at every stage
  - AG-UI streaming gave real-time transparency into the agent's reasoning
  - Evidence-grounded recommendations with inline citations built trust
  - HITL refinement via natural language gave CSMs control without complexity
- [ ] Write the **What Didn't / Challenges** section:
  - Simulated data limits the realism of insights (only 5 accounts, single quarter)
  - LLM latency in sequential 4-node pipeline (Quant -> Qual -> Strategist -> Editor)
  - Temperature tuning across agents required iteration
  - Refinement loop is single-turn (no multi-turn conversation memory)
- [ ] Write the **What's Next** section:
  - Connect to live monday.com boards via monday API for real account data
  - monday.com automation recipe: *"When status changes to 'QBR Prep', trigger generation and attach to item updates"*
  - Parallel execution of Quant + Qual agents (LangGraph supports this natively)
  - Multi-quarter trend analysis by storing historical QBR outputs
  - Add visual charts/graphs embedded in the QBR output (usage trends, NPS over time)
  - Model comparison: test Claude vs GPT-4 for each agent role
  - Multi-turn refinement with conversation memory
- [ ] Write the **How I'd Measure Success** section:
  - A/B test: CSM satisfaction scores comparing AI-drafted vs manual QBRs
  - Time-to-QBR: track reduction from 5+ hours to target ~15 minutes
  - Recommendation adoption rate: % of AI-suggested next steps that CSMs keep in final draft
  - Output consistency: cross-account comparison of QBR structure and completeness
- [ ] Save as `docs/experiment_and_reflection.md`

---

## Acceptance Criteria

- [ ] `docs/flow_architecture_diagram.md` exists with a Mermaid diagram covering the full data-to-output pipeline
- [ ] The diagram includes all layers: data source, API, agent pipeline (4 nodes with I/O schemas), AG-UI streaming, frontend, and HITL loop
- [ ] `docs/experiment_and_reflection.md` exists as a ~1-page document covering what worked, what didn't, what's next, and measurement approach
- [ ] Reflection references specific implementation details (not generic AI platitudes)
- [ ] All terminology matches the assignment dataset definitions

---

## Technical Decisions

_No decisions yet._

---

## Dependencies Detail

### `02_agent_framework.md`

- **What is needed:** A compiled LangGraph graph that can export its structure via `.get_graph().draw_mermaid()`.
- **Expected interface/contract:** The graph object is importable from `backend/app/agents/graph.py` and has 4 nodes with defined edges.

### `03_backend_api.md` + `04_frontend.md`

- **What is needed:** A fully working end-to-end application to reflect on honestly.
- **Expected interface/contract:** The full flow (select account -> generate QBR -> review -> refine) works from the deployed or local application.

### `06_documentation.md`

- **What is needed:** Design Brief and Prompts docs should be completed first so that the reflection can reference them.
- **Expected interface/contract:** `docs/design_brief.md` and `docs/prompts_documentation.md` exist.

---

## Log

_No entries yet._
