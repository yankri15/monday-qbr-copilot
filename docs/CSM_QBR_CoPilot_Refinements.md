# monday.com QBR Co-Pilot: CSM Refinement Pillars

This document captures the additional refinement pillars added after the initial PoC build, with a specific focus on making the product feel credible, valuable, and demo-ready for a monday.com Customer Success Manager.

The goal of these refinements was not to add AI for its own sake. The goal was to improve the actual CSM outcome:
- generate a stronger first QBR draft
- make the reasoning more trustworthy
- let the CSM steer the output before generation
- make the result easier to review, refine, and share

---

## 1. What Was Added

### 1. Per-agent model routing

Different parts of the workflow now use different model classes:
- extractor-style nodes use a faster, lighter model
- reasoning and writing nodes use a stronger model

This keeps the workflow efficient while preserving quality where it matters most.

Files:
- [backend/app/agents/llm.py](/Users/yankri/Documents/Monday/backend/app/agents/llm.py:1)
- [.env.example](/Users/yankri/Documents/Monday/.env.example:1)

### 2. CSM judge quality gate

A dedicated judge node now runs between strategy synthesis and final draft writing.

Its purpose is to review whether the strategy is actually acceptable from a CSM perspective:
- retention / expansion framing
- actionability
- evidence grounding
- monday.com product language
- no hallucinated promises

If the strategy is too weak, the graph retries the strategist with critique before allowing the editor to write the final draft.

Files:
- [backend/app/agents/csm_judge.py](/Users/yankri/Documents/Monday/backend/app/agents/csm_judge.py:1)
- [backend/app/agents/graph.py](/Users/yankri/Documents/Monday/backend/app/agents/graph.py:1)
- [frontend/src/components/ThoughtProcessPanel.tsx](/Users/yankri/Documents/Monday/frontend/src/components/ThoughtProcessPanel.tsx:1)

### 3. monday.com-aligned prompt refinement

The prompts were rewritten so the draft reads like a monday.com CSM prepared it, not like a generic SaaS summary.

This includes:
- monday.com Work OS vocabulary
- clearer retention vs expansion framing
- operational next steps
- stronger business-outcome mapping
- guardrails against roadmap promises or discount-style hallucinations

Files:
- [backend/app/agents/quant_agent.py](/Users/yankri/Documents/Monday/backend/app/agents/quant_agent.py:1)
- [backend/app/agents/qual_agent.py](/Users/yankri/Documents/Monday/backend/app/agents/qual_agent.py:1)
- [backend/app/agents/strategist.py](/Users/yankri/Documents/Monday/backend/app/agents/strategist.py:1)
- [backend/app/agents/editor.py](/Users/yankri/Documents/Monday/backend/app/agents/editor.py:1)
- [backend/app/agents/refiner.py](/Users/yankri/Documents/Monday/backend/app/agents/refiner.py:1)

### 4. Draft controls before generation

The CSM can now steer the report before generation through two control groups:
- `Focus areas`
- `Audience tone`

This turns the experience from “one generic draft” into “a guided draft generator the CSM can shape.”

Files:
- [frontend/src/components/QBRControls.tsx](/Users/yankri/Documents/Monday/frontend/src/components/QBRControls.tsx:1)
- [frontend/src/components/AccountWorkspace.tsx](/Users/yankri/Documents/Monday/frontend/src/components/AccountWorkspace.tsx:1)
- [backend/app/models/api.py](/Users/yankri/Documents/Monday/backend/app/models/api.py:1)

### 5. Upload customer data

The dashboard now supports uploading customer datasets in `.xlsx` or `.csv` format.

This makes the PoC feel less like a fixed demo and more like a real working tool:
- uploaded accounts appear in the account list
- uploaded accounts are visually marked
- uploaded accounts can be used directly in QBR generation

Files:
- [backend/app/routes/upload.py](/Users/yankri/Documents/Monday/backend/app/routes/upload.py:1)
- [backend/app/data/upload_store.py](/Users/yankri/Documents/Monday/backend/app/data/upload_store.py:1)
- [frontend/src/components/UploadZone.tsx](/Users/yankri/Documents/Monday/frontend/src/components/UploadZone.tsx:1)
- [frontend/src/components/AccountDashboard.tsx](/Users/yankri/Documents/Monday/frontend/src/components/AccountDashboard.tsx:1)

### 6. Export and sharing readiness

The final draft is no longer only a browser artifact.

It can now be exported as:
- Markdown
- PDF

The UI also exposes:
- a disabled `Send via Email` item as a clear future step

Files:
- [frontend/src/components/ExportMenu.tsx](/Users/yankri/Documents/Monday/frontend/src/components/ExportMenu.tsx:1)
- [frontend/src/lib/export.ts](/Users/yankri/Documents/Monday/frontend/src/lib/export.ts:1)
- [backend/app/routes/export.py](/Users/yankri/Documents/Monday/backend/app/routes/export.py:1)
- [backend/app/services/pdf_export.py](/Users/yankri/Documents/Monday/backend/app/services/pdf_export.py:1)

### 7. monday-first brand guardrails

One critical refinement was preventing third-party tool names from becoming the headline of the report.

For example, when the source notes mention `Jira`, the generated QBR should still remain clearly about monday.com value, monday.com workflows, monday.com integrations, and monday.com product adoption.

To enforce that:
- prompts were tightened
- a normalization layer was added
- regression coverage was added

Files:
- [backend/app/agents/brand_guardrails.py](/Users/yankri/Documents/Monday/backend/app/agents/brand_guardrails.py:1)
- [backend/app/agents/qual_agent.py](/Users/yankri/Documents/Monday/backend/app/agents/qual_agent.py:1)
- [backend/app/agents/strategist.py](/Users/yankri/Documents/Monday/backend/app/agents/strategist.py:1)
- [backend/app/agents/editor.py](/Users/yankri/Documents/Monday/backend/app/agents/editor.py:1)
- [backend/app/agents/refiner.py](/Users/yankri/Documents/Monday/backend/app/agents/refiner.py:1)

---

## 2. Draft Controls: How They Affect the QBR

These controls are not cosmetic. They change the generation path.

### Focus areas

`Focus areas` affects the `Strategist` node.

That means it changes:
- what gets prioritized
- what the recommendations emphasize
- what the CSM story is about

It does **not** only change wording. It changes the strategic weighting of the draft.

#### `Upsell Opportunity`

Expected effect:
- more expansion framing
- more adoption-growth language
- more advanced-feature positioning
- more cross-team rollout or champion-based growth recommendations

Observed effect in testing:
- the Altura Systems draft became more expansion-forward
- it leaned harder into analytics, broader rollout, internal champions, and integration workflows as growth levers

#### `Churn Risk`

Expected effect:
- more retention framing
- more urgency
- more rescue and stabilization actions
- more trust-repair language

Observed effect in testing:
- the Coral Retail draft became noticeably more retention-heavy
- it focused more explicitly on admin transition risk, active churn prevention, escalation handling, and immediate intervention

#### `Automation Adoption`

Expected effect:
- more enablement-oriented recommendations
- more focus on manual-work reduction
- more emphasis on workflow maturity and platform stickiness

Observed effect in testing:
- the Coral Retail draft shifted toward automation workshops, enablement, permissions training, and reducing manual work through monday.com Automations

### Audience tone

`Audience tone` affects the `Editor` node.

That means the underlying strategy can stay similar, but the final report voice changes for the intended audience.

#### `Executive`

Expected effect:
- business-level framing
- strategic language
- ROI and value realization
- less operational detail

Observed effect:
- the executive draft felt more summary-driven and business-oriented

#### `Team Lead`

Expected effect:
- operational language
- more workflow detail
- more references to Boards, Automations, and rollout actions
- more practical enablement steps

Observed effect:
- the Altura Systems team-lead draft became more execution-oriented and more focused on workshops, workflows, templates, and team-level rollout

#### `Technical`

Expected effect:
- more implementation detail
- more integration and data-flow language
- more system-level wording

Observed effect:
- the technical draft became more implementation-oriented and included more integration, data-flow, and Automation-logic language

---

## 3. What Was Tested

The following validations were performed.

### Automated verification

- backend unit tests:
  - agent workflow behavior
  - judge retry path
  - upload endpoint
  - merged account listing
  - export endpoint
  - latest-upload preference for duplicate account names
  - vendor-language normalization regression
- frontend verification:
  - `npm run lint`
  - `tsc --noEmit`

### Live behavior verification

Real OpenAI-backed generations were run to confirm that the controls actually shift the output:

- `Coral Retail`
  - baseline
  - `focus_areas=["churn_risk"]`
  - `focus_areas=["automation_adoption"]`
- `Altura Systems`
  - baseline
  - `focus_areas=["upsell_opportunity"]`
  - `tone="executive"`
  - `tone="team_lead"`
  - `tone="technical"`

### Export verification

- Markdown download triggered correctly from the UI
- PDF export returned a valid downloadable file from the backend
- export menu clipping in the editor was fixed so the menu is fully visible

### Upload verification

- uploaded CSV data was accepted by the backend
- uploaded accounts appeared in the dashboard with a visible distinction
- QBR generation used uploaded account data
- duplicate-name uploads now prefer the latest uploaded version

### monday-first language verification

A live Altura Systems generation was re-run after the brand guardrails were added.

Result:
- the final draft no longer surfaced `Jira`
- the report used monday-first wording such as:
  - `integration workflows`
  - `monday.com Integrations and Automations`
  - `development workflow connection`

---

## 4. Product Impact for the CSM

These refinements improve the actual CSM experience in four ways.

### Better first draft quality

The draft is more strategic, more evidence-grounded, and more aligned with monday.com language and value.

### Better control before generation

The CSM can intentionally steer:
- whether the story should feel more retention-oriented or expansion-oriented
- whether the report should sound more executive, operational, or technical

### Better trust in the output

The judge step and visible thought process make it easier for the CSM to understand why the report is taking a given direction.

### Better demo readiness

Uploads and export make the product feel closer to a real internal tool instead of a fixed assignment prototype.

---

## 5. Important Implementation Notes

### PDF rendering

The backend prefers WeasyPrint for richer PDF output.

In environments where native `glib/pango` libraries are unavailable, the service falls back to a lightweight pure-Python PDF path so export still works during demo and local testing.

### Copilot framing

The visible UX is now intentionally deliverable-first:
- the main story is preparing a strong QBR draft
- the co-pilot is the confidence and transparency layer, not the product headline

---

## 6. Summary

The additional refinement pillars transformed the project from a working PoC into a more credible CSM-facing draft workspace.

The key outcome is not just “more features.” The key outcome is that the CSM now has:
- better draft quality
- more control over the draft
- more trust in the reasoning
- more realistic ways to bring in data and export results
- stronger alignment with monday.com product language and demo expectations
