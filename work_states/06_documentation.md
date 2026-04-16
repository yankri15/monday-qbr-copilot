# Documentation (Design Brief + Prompts)

> Produce the written deliverables required by the assignment: Design Brief and Prompts & Components Documentation.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | Agent                          |
| Last Updated  | 2026-04-15                     |

### Dependencies

| Work State File            | Required Status | Notes                                            |
|----------------------------|-----------------|--------------------------------------------------|
| `02_agent_framework.md`    | `DONE`          | Need finalized prompts and schemas to document   |
| `03_backend_api.md`        | `DONE`          | Need working API to validate end-to-end flow     |
| `04_frontend.md`           | `DONE`          | Need working UI to screenshot and reference      |

---

## Objective

Create two assignment deliverables that exist as standalone documents alongside the working PoC. These are drafted *after* the prototype is complete and working smoothly — the content is extracted and polished from what already exists in the codebase. The documents should demonstrate thoughtful problem framing, deep prompt engineering awareness, and honest reflection on trade-offs.

---

## Plan

### Deliverable 1: Design Brief (1–2 pages)

Per the assignment: *"Overview explaining how you framed the problem, who the user is (CSM, team lead), and what success looks like. Include assumptions, limitations, prioritization and how you'd validate usefulness."*

- [x] Write the **Problem Framing** section:
  - CSMs spend 5+ hours per account preparing QBRs manually
  - Data is scattered across CRM notes, support tickets, usage metrics, and NPS
  - Inconsistent storytelling and missed insights across accounts
- [x] Write the **User Persona** section:
  - Primary: Customer Success Manager (CSM) — prepares QBRs for their book of business
  - Secondary: Team Lead / VP CS — reviews QBR quality and consistency across the team
- [x] Write the **Success Metrics** section:
  - Time-to-QBR reduced from 5+ hours to ~15 minutes of review
  - Recommendation coverage: every QBR includes data-grounded next steps
  - CSM trust: transparent reasoning with inline data citations
- [x] Write the **Assumptions & Limitations** section:
  - Simulated dataset (5 accounts, 13 fields) — not connected to live monday.com boards
  - Single-quarter snapshot — no historical trend analysis across multiple quarters
  - OpenAI as sole LLM provider — no model comparison or fallback
  - No authentication or multi-tenant support in the PoC
- [x] Write the **Prioritization** section:
  - P0: Core QBR generation pipeline with structured + unstructured data
  - P1: Real-time streaming UX (AG-UI) for transparency
  - P1: HITL refinement for trust and control
  - P2: Export/sharing, multi-quarter trends, live integrations
- [x] Write the **Validation Approach** section:
  - A/B test: CSM satisfaction comparing AI-drafted vs manually-drafted QBRs
  - Time tracking: measure prep time reduction per account
  - Recommendation quality: review by CS leadership for business relevance

### Deliverable 4: Prompts & Components Documentation

Per the assignment: *"Showing key prompts for insight extraction, summarization, and recommendations. Include how you handled hallucinations and structured outputs (schemas, temperature, format)."*

- [x] Document **each agent's prompt** (extract from actual codebase):
  - Quant Agent: metrics analysis prompt, input fields, expected output
  - Qual Agent: sentiment/theme extraction prompt, input fields, expected output
  - Strategist: synthesis prompt, cross-referencing approach, evidence-grounding instructions
  - Editor: formatting prompt, Markdown structure, citation instructions
  - Refiner: HITL refinement prompt, instruction-following approach
- [x] Document **hallucination prevention strategy**:
  - Pydantic structured output schemas (JSON mode) enforce field-level type safety
  - Separation of concerns: each agent sees only its relevant data slice
  - Evidence grounding: Strategist must cite specific metrics for each recommendation
  - Temperature settings and rationale for each agent
- [x] Document **structured output schemas** with examples:
  - `QuantInsights`: show the Pydantic model and a sample output
  - `QualInsights`: show the Pydantic model and a sample output
  - `StrategicSynthesis`: show the recommendation structure with evidence fields
- [x] Save as `docs/design_brief.md` and `docs/prompts_documentation.md`

---

## Acceptance Criteria

- [x] `docs/design_brief.md` exists and is 1–2 pages covering problem framing, user persona, success metrics, assumptions, limitations, prioritization, and validation approach
- [x] `docs/prompts_documentation.md` exists and documents all 6 agent prompts (including CSM Judge), hallucination prevention strategy, structured output schemas with examples, and temperature settings
- [x] Both documents reference the actual implementation (file paths, schema names) rather than being abstract
- [x] All field-specific terminology matches the assignment dataset definitions (SCAT = Success Confidence & Adoption Trend 0–100, risk_engine_score = AI-predicted churn risk 0–1, etc.)

---

## Technical Decisions

- Documented all 6 agents (including CSM Judge) rather than the 5 originally planned — the judge quality gate is a key architectural differentiator worth calling out.
- Included sample JSON outputs for each schema to make the documentation concrete rather than abstract.
- Used verbatim system prompts from the codebase rather than paraphrased summaries.

---

## Dependencies Detail

### `02_agent_framework.md`

- **What is needed:** Finalized prompts for all 5 agents (Quant, Qual, Strategist, Editor, Refiner) and the Pydantic output schemas (`QuantInsights`, `QualInsights`, `StrategicSynthesis`).
- **Expected interface/contract:** Prompts and schemas are defined in `backend/app/agents/` and can be extracted/referenced directly.

### `03_backend_api.md` + `04_frontend.md`

- **What is needed:** A working end-to-end flow to validate that the documented components actually produce correct output.
- **Expected interface/contract:** The full pipeline runs successfully for at least 2-3 accounts, producing coherent QBR drafts.

---

## Log

- **2026-04-15:** Created `docs/design_brief.md` (problem framing, personas, success metrics, assumptions/limitations, prioritization, validation approach) and `docs/prompts_documentation.md` (architecture overview with mermaid diagram, all 6 agent prompts with verbatim system prompts, model/temperature configs, hallucination prevention strategy across 6 layers, structured output schemas with sample JSON). Both reference actual codebase paths and use assignment-defined field semantics. Marked DONE.
