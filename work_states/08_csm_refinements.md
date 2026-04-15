# CSM Refinement & Quality Uplift

> Upgrade the QBR Co-Pilot from a working PoC to a CSM-ready tool: per-agent model configuration, LLM-as-a-Judge quality gate, monday.com-aligned prompts, UI controls for focus/tone/upload, and export/delivery options (PDF, Markdown, email).

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | `Codex`                        |
| Last Updated  | 2026-04-15                     |

### Dependencies

| Work State File              | Required Status |
|------------------------------|-----------------|
| `00_infrastructure.md`       | `DONE`          |
| `01_data_layer.md`           | `DONE`          |
| `02_agent_framework.md`      | `DONE`          |
| `03_backend_api.md`          | `DONE`          |
| `04_frontend.md`             | `DONE`          |

---

## Objective

Transform the QBR Co-Pilot from a generic PoC into a tool that a monday.com CSM can trust for real QBR preparation. When done, the generated QBR reads as a strategic CSM narrative (not a data dump), every insight is validated against product acceptance criteria before delivery, the CSM can control the focus and tone of each QBR, the tool accepts customer data beyond the bundled sample spreadsheet, and the finished QBR can be downloaded as a PDF or Markdown file (with email delivery as a future addition).

---

## Plan

### Pillar 1 — Per-Agent Model Configuration

> **Goal:** Allow each agent node to use a different LLM model so extractors can stay fast/cheap while thinkers use a more capable model.

- [x] **1.1** Add an `model` parameter (default `None`) to `invoke_structured_output()` and `invoke_text_output()` in `backend/app/agents/llm.py`. When `None`, fall back to the existing `_get_model_name()` resolution. When provided, use the caller-supplied model name directly.
- [x] **1.2** Extend `build_chat_model()` to accept an optional `model: str | None` parameter. If `None`, resolve via `_get_model_name()`. If provided, pass it to `ChatOpenAI(model=model, ...)`.
- [x] **1.3** Add a module-level config dict `AGENT_MODEL_CONFIG` in `llm.py` mapping logical agent roles to model names, loaded from env vars with sensible defaults:
  ```
  AGENT_MODEL_CONFIG = {
      "extractor": os.getenv("OPENAI_MODEL_EXTRACTOR", "gpt-4.1-mini"),
      "thinker":   os.getenv("OPENAI_MODEL_THINKER",   "gpt-4.1"),
  }
  ```
- [x] **1.4** Update `quant_agent.py` and `qual_agent.py` to pass `model=AGENT_MODEL_CONFIG["extractor"]` to their `invoke_structured_output()` calls.
- [x] **1.5** Update `strategist.py` to pass `model=AGENT_MODEL_CONFIG["thinker"]` and `temperature=0.3` (up from `0.0`) to its `invoke_structured_output()` call.
- [x] **1.6** Update `editor.py` to pass `model=AGENT_MODEL_CONFIG["thinker"]` to its `invoke_text_output()` call. Keep `temperature=0.2`.
- [x] **1.7** Update `refiner.py` to pass `model=AGENT_MODEL_CONFIG["thinker"]` to its `invoke_text_output()` call. Keep `temperature=0.3`.
- [x] **1.8** Add `OPENAI_MODEL_EXTRACTOR` and `OPENAI_MODEL_THINKER` to `.env.example` with placeholder values.
- [x] **1.9** Verify: run the pipeline for one account and confirm from logs/debug that the Strategist and Editor use the thinker model while Quant and Qual use the extractor model.

### Pillar 2 — LLM-as-a-Judge Quality Gate

> **Goal:** Insert a CSM evaluator node between the Strategist and Editor. If the Strategist output fails the CSM acceptance rubric, loop it back with critique for a retry (max 2 retries).

- [x] **2.1** Add new fields to `WorkflowState` in `backend/app/agents/state.py`:
  ```python
  judge_verdict: dict[str, Any]     # Serialized JudgeVerdict
  judge_retry_count: int            # Current retry iteration (starts at 0)
  judge_critique: str               # Accumulated critique for strategist re-prompting
  ```
- [x] **2.2** Add a `JudgeVerdict` schema to `backend/app/agents/schemas.py`:
  ```python
  class JudgeVerdict(BaseModel):
      model_config = ConfigDict(extra="forbid")

      passed: bool = Field(description="Whether the synthesis meets CSM acceptance criteria")
      critique: str = Field(description="Specific feedback if failed; 'Approved' if passed")
      scores: dict[str, int] = Field(
          description="Rubric scores (1-10) for: retention_focus, expansion_focus, "
                      "actionability, evidence_grounding, monday_language"
      )
  ```
- [x] **2.3** Create `backend/app/agents/csm_judge.py` with:
  - A system prompt grounded in CSM acceptance criteria:
    ```
    You are a senior Customer Success quality reviewer at monday.com.
    Evaluate the strategic synthesis against these mandatory criteria:

    1. RETENTION & EXPANSION LENS: Does the synthesis explicitly frame insights
       through customer retention (preventing churn) or expansion (upselling
       seats, tiers, or features)? Every recommendation must serve one of these goals.
    2. ACTIONABILITY: Are the recommended next steps specific and executable?
       Vague advice like "improve engagement" fails. Acceptable: "Schedule a
       tailored automation workshop for the team lead via {preferred_channel}."
    3. EVIDENCE GROUNDING: Does every claim reference a concrete metric or
       qualitative signal from the source data? Flag any ungrounded statements.
    4. MONDAY.COM PRODUCT LANGUAGE: Does the output use monday.com Work OS
       vocabulary (Boards, Automations, Integrations, Workspaces, Dashboards)
       rather than generic SaaS terms?
    5. NO HALLUCINATED PROMISES: The output must NOT promise roadmap features,
       offer discounts, or reference capabilities beyond the provided data.

    Score each criterion 1-10. Pass threshold: all scores >= 6 AND average >= 7.
    If any criterion scores below 6 or the average is below 7, fail the review
    and provide precise, actionable critique the Strategist can use to improve.
    ```
  - A `generate_judge_verdict()` function that takes the `StrategicSynthesis` JSON plus the original account data and returns a `JudgeVerdict`.
  - A `run_csm_judge(state: WorkflowState)` LangGraph node that:
    - Calls `generate_judge_verdict()`
    - Increments `judge_retry_count`
    - Stores `judge_verdict` and `judge_critique` in state
    - Returns the updated state dict
- [x] **2.4** Add a routing function `judge_router(state: WorkflowState) -> str` in `csm_judge.py`:
  ```python
  MAX_JUDGE_RETRIES = 2

  def judge_router(state: WorkflowState) -> str:
      verdict = JudgeVerdict.model_validate(state["judge_verdict"])
      if verdict.passed:
          return "editor"
      if state.get("judge_retry_count", 0) >= MAX_JUDGE_RETRIES:
          return "editor"  # proceed anyway after max retries
      return "strategist"
  ```
- [x] **2.5** Update `backend/app/agents/strategist.py` to accept optional `judge_critique` from state. If present, append it to the user prompt:
  ```
  --- REVIEWER FEEDBACK (address all points) ---
  {state["judge_critique"]}
  ```
- [x] **2.6** Rewire the graph in `backend/app/agents/graph.py`:
  - Add node: `builder.add_node("csm_judge", run_csm_judge)`
  - Replace the `strategist -> editor` edge with:
    ```python
    builder.add_edge("strategist", "csm_judge")
    builder.add_conditional_edges("csm_judge", judge_router)
    ```
  - Remove the direct `builder.add_edge("strategist", "editor")` line.
- [x] **2.7** Update `STEP_MESSAGES` in `backend/app/routes/qbr.py` to include the judge node:
  ```python
  "csm_judge": "Evaluating QBR quality against CSM acceptance criteria...",
  ```
- [x] **2.8** Update `STREAMED_STATE_KEYS` in `qbr.py` to include `"judge_verdict"` so the frontend receives the rubric scores.
- [x] **2.9** Update the frontend `StepName` type in `frontend/src/lib/types.ts` to include `"csm_judge"`.
- [x] **2.10** Add a judge step entry to `createSteps()` in `frontend/src/components/AccountWorkspace.tsx` (between strategist and editor).
- [x] **2.11** Update the `ThoughtProcessPanel` component to render the judge verdict and rubric scores when the `judge_verdict` state delta arrives. Display pass/fail status and the individual criterion scores.
- [x] **2.12** Update existing tests in `backend/tests/test_agent_framework.py`:
  - Mock `generate_judge_verdict` to return a passing verdict.
  - Verify the pipeline now emits 5 `STEP_STARTED` / `STEP_FINISHED` pairs (quant, qual, strategist, judge, editor).
  - Add a test for the retry path: mock the judge to fail once, then pass, and verify the strategist runs twice.

### Pillar 3 — CSM-Aligned Prompt Refinement

> **Goal:** Rewrite all agent system prompts to produce output that reads like a real monday.com CSM prepared it, grounded in product-specific terminology, retention/expansion strategy, and actionable recommendations.

- [x] **3.1** Rewrite `QUANT_SYSTEM_PROMPT` in `backend/app/agents/quant_agent.py`:
  - Explain what each monday.com-specific metric means in context:
    - `scat_score` = Success Confidence & Adoption Trend (0-100, higher is healthier)
    - `automation_adoption_pct` = proportion of available Automations used; low adoption signals manual-heavy workflows and reduced Work OS stickiness
    - `risk_engine_score` = AI-predicted churn probability (0-1); above 0.6 triggers proactive intervention
  - Instruct the agent to flag when automation adoption is below 30% as a key risk signal
  - Instruct the agent to call out the delta in `usage_growth_qoq` as the primary conversation driver
- [x] **3.2** Rewrite `QUAL_SYSTEM_PROMPT` in `backend/app/agents/qual_agent.py`:
  - Add instructions to identify champion signals (mentions of internal advocates, power users, executive sponsors)
  - Add instructions to detect churn risk language (complaints about competitors, requests for features that exist in other tools, frustration with onboarding)
  - Add instructions to flag feature requests that align with existing monday.com capabilities the customer may not be using
- [x] **3.3** Major rewrite of `STRATEGIST_SYSTEM_PROMPT` in `backend/app/agents/strategist.py`:
  - Frame the agent as a senior CSM at monday.com preparing strategic recommendations
  - Mandate every insight be framed through a Retention or Expansion lens
  - Require monday.com product vocabulary throughout: Boards, Automations, Integrations, Workspaces, Dashboards, Work OS
  - Require connecting metrics to business outcomes (e.g., "low automation adoption -> team is doing manual work that Automations could handle -> reduced platform value -> churn risk")
  - Require cross-sell recommendations to reference specific monday.com features/tiers (e.g., "Their current Pro plan lacks Dashboard-level permissions — upgrading to Enterprise would unlock governance controls their IT team requested in CRM notes")
  - If `focus_areas` are provided in state (from Pillar 4), prioritize those areas in the synthesis
  - If `judge_critique` is provided in state (from Pillar 2), address every point in the feedback
- [x] **3.4** Rewrite `EDITOR_SYSTEM_PROMPT` in `backend/app/agents/editor.py`:
  - Instruct the editor to produce a narrative, not a bullet-point dump: each section should tell a cohesive story that flows from the data to the recommendation
  - If a `tone` parameter is provided in state (from Pillar 4), adapt the writing style:
    - `"executive"`: high-level strategic language, minimal technical detail, focus on business impact and ROI
    - `"team_lead"`: operational focus, workflow-specific recommendations, mention specific Boards/Automations
    - `"technical"`: include integration details, API usage patterns, Automation trigger/action specifics
  - Default tone is `"executive"` if none specified
  - Use monday.com product language throughout the draft
  - Ensure the "Next Steps" section contains calendar-ready action items with suggested owners and timelines
- [x] **3.5** Update `REFINER_SYSTEM_PROMPT` in `backend/app/agents/refiner.py`:
  - Add explicit guardrails: "You must NOT promise unreleased features, offer pricing discounts, or make commitments on behalf of monday.com. If the user's instructions ask for any of these, politely note that these require approval from the account team and revise accordingly."
  - Add instruction to preserve monday.com product vocabulary even when rephrasing

### Pillar 4 — UI/UX Enhancements

> **Goal:** Give the CSM control over QBR generation (focus areas, audience tone) and allow uploading custom customer data files.

#### 4a — Focus Toggles & Tone Selector (Backend)

- [x] **4a.1** Extend `GenerateQBRRequest` in `backend/app/models/api.py`:
  ```python
  focus_areas: list[str] = Field(
      default_factory=list,
      description="Optional focus areas: 'upsell_opportunity', 'churn_risk', 'automation_adoption'"
  )
  tone: str = Field(
      default="executive",
      description="Audience tone: 'executive', 'team_lead', or 'technical'"
  )
  ```
- [x] **4a.2** Pass `focus_areas` and `tone` through the SSE generation flow in `backend/app/routes/qbr.py`:
  - Include them in the initial `WorkflowState` passed to the graph: `{"account": ..., "focus_areas": payload.focus_areas, "tone": payload.tone}`
- [x] **4a.3** Extend `WorkflowState` in `state.py` with:
  ```python
  focus_areas: list[str]
  tone: str
  ```
- [x] **4a.4** Update the Strategist node to read `state.get("focus_areas", [])` and inject a focus directive into the user prompt when non-empty:
  ```
  --- CSM FOCUS PRIORITIES ---
  The CSM has requested emphasis on: {', '.join(focus_areas)}.
  Weight your analysis and recommendations toward these areas.
  ```
- [x] **4a.5** Update the Editor node to read `state.get("tone", "executive")` and inject it into the user prompt so the writing style adapts to the selected audience.

#### 4b — Focus Toggles & Tone Selector (Frontend)

- [x] **4b.1** Add `focus_areas` and `tone` to the `GenerateQbrPayload` type in `frontend/src/lib/types.ts`.
- [x] **4b.2** Update `generateQBR()` in `frontend/src/lib/api.ts` to accept and pass `focus_areas` and `tone` in the request body.
- [x] **4b.3** Create a `QBRControls` component (`frontend/src/components/QBRControls.tsx`) with:
  - Three toggle chips for focus areas: "Upsell Opportunity", "Churn Risk", "Automation Adoption"
  - A segmented control / dropdown for tone: "Executive", "Team Lead", "Technical"
  - State managed locally; values passed up to `AccountWorkspace` via props/callbacks
- [x] **4b.4** Integrate `QBRControls` into `AccountWorkspace.tsx`:
  - Render it between the header bar and the "Draft QBR" button (or inside the header bar alongside the button)
  - Pass selected `focusAreas` and `tone` into the `generateQBR()` call in `handleGenerate()`
  - Reset controls when navigating between accounts

#### 4c — Dynamic Data Upload (Backend)

- [x] **4c.1** Create `backend/app/routes/upload.py` with a `POST /api/upload-data` endpoint:
  - Accept `UploadFile` (multipart form data)
  - Validate file extension is `.xlsx` or `.csv`
  - For `.xlsx`: reuse the same header validation logic from `loader.py` (extract into a shared `parse_customer_file()` helper)
  - For `.csv`: read with Python's `csv` module, validate headers match `EXPECTED_HEADERS`, validate each row through `CustomerAccount.model_validate()`
  - On validation success: store parsed accounts in an in-memory dict keyed by a generated upload ID
  - Return: `{"upload_id": str, "accounts": list[CustomerAccountResponse]}`
- [x] **4c.2** Extract shared parsing logic from `loader.py` into a `parse_rows()` helper that both the existing `_load_accounts()` and the upload endpoint can use. Keep the original `loader.py` working unchanged.
- [x] **4c.3** Create an in-memory upload store module `backend/app/data/upload_store.py`:
  - `add_uploaded_accounts(accounts: list[CustomerAccount]) -> str` — stores accounts, returns upload ID
  - `get_uploaded_account_by_name(name: str) -> CustomerAccount | None` — searches all uploaded data
  - `get_all_uploaded_accounts() -> list[CustomerAccount]`
  - `clear_uploads() -> None`
- [x] **4c.4** Update `GET /api/accounts` in `backend/app/routes/accounts.py` to return both sample accounts and any uploaded accounts (merged, with uploaded accounts marked via a response field or separate list).
- [x] **4c.5** Update `get_account_by_name` usage in `backend/app/routes/qbr.py` to also search uploaded accounts if not found in the sample data.
- [x] **4c.6** Register the upload router in `backend/app/routes/__init__.py`.

#### 4d — Dynamic Data Upload (Frontend)

- [x] **4d.1** Create an `UploadZone` component (`frontend/src/components/UploadZone.tsx`):
  - Drag-and-drop zone + file input button
  - Accept `.xlsx` and `.csv` files only
  - On drop/select: POST to `/api/upload-data` as multipart form data
  - Show upload progress, validation errors, and success state
  - On success: call a callback to refresh the account list
- [x] **4d.2** Integrate `UploadZone` into `AccountDashboard.tsx`:
  - Render it above or alongside the account grid
  - On successful upload, merge new accounts into the displayed list
  - Add a visual badge or separator distinguishing uploaded accounts from sample accounts

### Pillar 5 — Export & Delivery

> **Goal:** Once the CSM is satisfied with the generated QBR, provide options to download it as a PDF or Markdown file, and (future) send it via email.

#### 5a — Markdown File Download (Frontend-only)

- [x] **5a.1** Add a `downloadMarkdown(draft: string, accountName: string)` helper to `frontend/src/lib/export.ts`:
  - Create a `Blob` from the draft string with MIME type `text/markdown`
  - Generate an object URL via `URL.createObjectURL()`
  - Programmatically create and click a hidden `<a>` element with `download="{accountName}_QBR.md"`
  - Revoke the object URL after download triggers

#### 5b — PDF Download (Backend + Frontend)

- [x] **5b.1** Add `weasyprint` and `markdown` to `backend/pyproject.toml` dependencies and run `uv sync`.
- [x] **5b.2** Create `backend/app/services/pdf_export.py` with a `markdown_to_pdf(markdown_content: str, account_name: str) -> bytes` function:
  - Convert the markdown string to HTML using the `markdown` library (with `tables` and `fenced_code` extensions)
  - Wrap the HTML in a minimal styled template with professional typography, monday.com brand colors for headings, proper page margins, and a header/footer with the account name and generation date
  - Render to PDF bytes using `weasyprint.HTML(string=html).write_pdf()`
- [x] **5b.3** Add a `POST /api/export-pdf` endpoint in `backend/app/routes/export.py`:
  - Request body: `ExportPdfRequest` with fields `markdown_content: str` (min_length=1) and `account_name: str` (min_length=1)
  - Call `markdown_to_pdf()` and return the result as a `Response` with `media_type="application/pdf"` and `Content-Disposition: attachment; filename="{account_name}_QBR.pdf"` header
  - Handle errors (e.g., weasyprint rendering failure) with a 500 response and descriptive message
- [x] **5b.4** Add request/response models to `backend/app/models/api.py`:
  ```python
  class ExportPdfRequest(BaseModel):
      model_config = ConfigDict(extra="forbid")
      markdown_content: str = Field(min_length=1, description="Markdown QBR draft to convert to PDF")
      account_name: str = Field(min_length=1, description="Account name for the PDF filename")
  ```
- [x] **5b.5** Register the export router in `backend/app/routes/__init__.py`.
- [x] **5b.6** Add an `exportPdf(markdownContent: string, accountName: string)` function to `frontend/src/lib/api.ts`:
  - POST to `/api/export-pdf` with the markdown content and account name
  - Receive the response as a `Blob`
  - Trigger a browser download using the same object URL + hidden `<a>` pattern as the Markdown download

#### 5c — Export Menu (Frontend UI)

- [x] **5c.1** Replace the single "Export" button in `frontend/src/components/QBREditor.tsx` with an `ExportMenu` dropdown component:
  - Three options: "Download as Markdown", "Download as PDF", "Send via Email" (disabled, with a "Coming soon" tooltip)
  - The dropdown appears on click, closes on outside click or selection
  - "Download as Markdown" calls `downloadMarkdown()` from `export.ts`
  - "Download as PDF" calls `exportPdf()` from `api.ts`, shows a brief loading state while the backend renders
  - "Send via Email" is rendered as disabled/greyed out with a tooltip or label indicating future availability
- [x] **5c.2** Pass the `accountName` prop into `QBREditor` (from `AccountWorkspace`) so downloads use the correct filename.

#### 5d — Email Delivery (Future — TODO)

- [ ] **5d.1** _(FUTURE)_ Design and implement email delivery: integrate an email service (SMTP or a provider like SendGrid/Resend), add a `POST /api/send-qbr-email` endpoint that accepts a recipient address and the QBR draft, renders the PDF server-side, and sends it as an attachment. Add a modal in the frontend for entering the recipient email. Enable the "Send via Email" option in the export menu.

---

## Acceptance Criteria

### Pillar 1 — Model Configuration
- [x] `invoke_structured_output()` and `invoke_text_output()` accept an optional `model` parameter
- [x] Running the pipeline logs show the Strategist using the "thinker" model and the Quant Agent using the "extractor" model
- [x] `.env.example` documents `OPENAI_MODEL_EXTRACTOR` and `OPENAI_MODEL_THINKER`
- [x] All existing tests pass with the updated signatures (backward compatible defaults)

### Pillar 2 — LLM-as-a-Judge
- [x] The LangGraph graph includes a `csm_judge` node between `strategist` and `editor`
- [x] When the judge returns `passed=True`, the pipeline proceeds directly to `editor`
- [x] When the judge returns `passed=False`, the pipeline routes back to `strategist` with the critique in state
- [x] After `MAX_JUDGE_RETRIES` (2) failures, the pipeline proceeds to `editor` regardless
- [x] The frontend displays the judge step in the ThoughtProcessPanel with rubric scores
- [x] SSE stream emits `STEP_STARTED` / `STEP_FINISHED` events for the `csm_judge` node
- [x] `judge_verdict` state delta is streamed to the frontend

### Pillar 3 — Prompt Refinement
- [x] The Quant Agent system prompt explains `scat_score`, `automation_adoption_pct`, and `risk_engine_score` in monday.com context
- [x] The Qual Agent system prompt identifies champion signals and churn risk language
- [x] The Strategist system prompt mandates Retention/Expansion framing, monday.com vocabulary, and metric-to-outcome connections
- [x] The Editor system prompt produces a narrative (not a bullet dump) and adapts tone to the audience
- [x] The Refiner system prompt blocks hallucinated promises (roadmap features, discounts)
- [x] Generated QBR drafts use monday.com terminology: Boards, Automations, Integrations, Workspaces

### Pillar 4 — UI/UX
- [x] `POST /api/generate-qbr` accepts optional `focus_areas` and `tone` fields
- [x] Passing `focus_areas=["churn_risk"]` produces a QBR draft that emphasizes churn prevention
- [x] Passing `tone="team_lead"` produces a QBR draft with operational/workflow language instead of executive language
- [x] `POST /api/upload-data` accepts an `.xlsx` file with the 13-column schema and returns parsed accounts
- [x] `POST /api/upload-data` rejects files with mismatched headers (returns 422 with a descriptive error)
- [x] `GET /api/accounts` returns both sample and uploaded accounts
- [x] The frontend renders focus toggles and a tone selector before QBR generation
- [x] The frontend renders a file drop zone on the dashboard
- [x] Uploaded accounts appear in the account grid with a visual distinction from sample accounts

### Pillar 5 — Export & Delivery
- [x] Clicking "Download as Markdown" in the export menu triggers a browser download of a `.md` file containing the current draft
- [x] The downloaded Markdown file is named `{account_name}_QBR.md`
- [x] `POST /api/export-pdf` accepts a markdown string and account name, returns a valid PDF binary
- [x] The returned PDF renders the QBR with proper typography, headings, and page layout
- [x] Clicking "Download as PDF" in the export menu triggers a browser download of a `.pdf` file
- [x] The "Send via Email" option is visible but disabled with a "Coming soon" indicator
- [x] The export menu replaces the old single "Export" (clipboard-only) button
- [x] `weasyprint` and `markdown` are listed in `backend/pyproject.toml` dependencies

---

## Technical Decisions

> Append-only. Format: `[DECISION] <date>: <description> — Rationale: <why>`

- [DECISION] 2026-04-15: Sequence this work state in two passes: UI/UX polish first, backend-heavy quality and export pillars second. — Rationale: the recruiter demo depends most on the product story, visual hierarchy, and polished CSM workflow framing; deeper backend upgrades can land immediately after the demo-facing surface is aligned.
- [DECISION] 2026-04-15: Represent judge rubric scores as a fixed `JudgeScores` object rather than a free-form `dict[str, int]` at the schema layer. — Rationale: OpenAI structured output in the current LangChain stack handled a fixed object schema reliably during live runs, while the free-form dict shape caused runtime validation/compatibility issues.
- [DECISION] 2026-04-15: Keep `weasyprint` as the preferred PDF renderer, but fall back to a lightweight pure-Python PDF path when native `glib/pango` libraries are unavailable in the local environment. — Rationale: the work state requires backend PDF export for the demo, while this machine does not currently provide the native libraries that WeasyPrint expects at runtime.

---

## Dependencies Detail

### `02_agent_framework.md`

- **What is needed:** The existing LangGraph graph assembly in `graph.py`, all agent node functions, the `WorkflowState` TypedDict, and the Pydantic output schemas in `schemas.py`.
- **Expected interface/contract:** `get_qbr_graph()` returns a compiled `StateGraph`. Each node function accepts `WorkflowState` and returns a partial dict. `WorkflowState` is a `TypedDict(total=False)` that we will extend with new keys (`judge_verdict`, `judge_retry_count`, `judge_critique`, `focus_areas`, `tone`).

### `03_backend_api.md`

- **What is needed:** The FastAPI route handlers in `qbr.py` and `accounts.py`, the request/response models in `api.py`, and the SSE encoding/streaming infrastructure.
- **Expected interface/contract:** `GenerateQBRRequest` is extended with optional `focus_areas` and `tone`. The SSE stream already handles `STEP_STARTED`/`STEP_FINISHED` for any named node — adding `csm_judge` requires only a new entry in `STEP_MESSAGES`. The upload endpoint is a new route registered via `api_router`.

### `01_data_layer.md`

- **What is needed:** The Excel parser in `loader.py` and the `CustomerAccount` Pydantic model.
- **Expected interface/contract:** The upload feature reuses `EXPECTED_HEADERS` and `CustomerAccount.model_validate()` for data validation. We extract a shared `parse_rows()` helper from `loader.py` to avoid duplicating validation logic. The `CustomerAccount` model itself is unchanged.

### `04_frontend.md`

- **What is needed:** The `AccountWorkspace`, `AccountDashboard`, `ThoughtProcessPanel` components, the `types.ts` type definitions, and the `api.ts` fetch helpers.
- **Expected interface/contract:** `StepName` union type is extended with `"csm_judge"`. `GenerateQbrPayload` is extended with `focus_areas` and `tone`. `generateQBR()` passes these through the request body. Two new components (`QBRControls`, `UploadZone`) are integrated into existing pages.

### Pillar 5 — Export Dependencies

- **What is needed (backend):** The `weasyprint` library (system dependency: requires `pango`, `cairo`, and `gdk-pixbuf` — available via Homebrew on macOS: `brew install pango`). The `markdown` Python library for Markdown-to-HTML conversion. Both added to `pyproject.toml`.
- **What is needed (frontend):** The existing `QBREditor` component which currently has a clipboard-only "Export" button. The `accountName` must be threaded from `AccountWorkspace` into `QBREditor` as a new prop for filename generation.
- **Expected interface/contract:** `POST /api/export-pdf` accepts `{"markdown_content": str, "account_name": str}` and returns `application/pdf` bytes. The frontend `exportPdf()` function fetches this as a blob and triggers a download. The `downloadMarkdown()` function is entirely client-side with no backend dependency.

---

## Log

> Chronological, append-only. Format: `[<STATUS>] <timestamp>: <what happened>`
> Statuses: `START`, `PROGRESS`, `BLOCKER`, `RESOLVED`, `DONE`

- [START] 2026-04-15: Began `08_csm_refinements` by reviewing the new work state, the plan docs, and the live frontend to identify where the current UI over-emphasized the co-pilot layer instead of the CSM deliverable.
- [PROGRESS] 2026-04-15: Confirmed sequencing with the user: prioritize a recruiter-demo-ready UI/UX pass first, then move to the heavier backend pillars (model routing, judge loop, uploads, export).
- [PROGRESS] 2026-04-15: Refined the dashboard and account workspace copy, hierarchy, and section naming so the visible story is “prepare a strong QBR draft fast” while the co-pilot remains the transparency/wow layer.
- [PROGRESS] 2026-04-15: Implemented per-agent model routing, monday.com-aligned prompt rewrites, the CSM judge loop, focus/tone request plumbing, and frontend controls for steering QBR generation.
- [RESOLVED] 2026-04-15: Fixed a live runtime issue in the judge step by replacing the free-form rubric score dict schema with a fixed score object schema compatible with OpenAI structured outputs in the current stack.
- [PROGRESS] 2026-04-15: Verified the updated backend/frontend slice with backend unit tests, frontend lint/typecheck, and a live browser flow showing five streamed steps, judge rubric scores, and a completed draft.
- [PROGRESS] 2026-04-15: Added dynamic customer-data upload across backend and frontend, including shared file parsing, in-memory uploaded-account storage, dashboard upload UX, and uploaded-account badges in the grid/workspace.
- [PROGRESS] 2026-04-15: Added Markdown and PDF export, replaced the clipboard-only action with an export menu, and exposed a disabled email-delivery placeholder to match the next planned product step.
- [RESOLVED] 2026-04-15: Verified upload and export locally: `/api/upload-data` accepted a CSV demo account, `/api/accounts` returned uploaded accounts with source metadata, `/api/export-pdf` returned a valid single-page PDF, frontend lint/typecheck passed, backend tests passed, and Playwright snapshots showed the upload zone plus export-ready workspace UI.
- [RESOLVED] 2026-04-15: Ran live control verification against OpenAI-backed generations. `focus_areas=["churn_risk"]` produced a more retention-heavy Coral Retail draft, `focus_areas=["automation_adoption"]` shifted the same account toward enablement/automation recovery, `focus_areas=["upsell_opportunity"]` made Altura Systems more expansion-forward, and tone variants (`executive`, `team_lead`, `technical`) changed the Altura draft from strategic language to operational workflow guidance to integration/data-flow detail.
- [DONE] 2026-04-15: Closed `08_csm_refinements` after final UI/dev-environment polish. Verified the dashboard loads sample data cleanly on both `localhost:3001` and `127.0.0.1:3001`, with the recruiter-demo-ready CSM workflow, controls, uploads, exports, and monday-first guardrails all in place.
