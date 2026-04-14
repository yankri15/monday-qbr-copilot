# Frontend (Next.js)

> Build the QBR Co-Pilot UI: account selector, streaming generation view, interactive Markdown editor, and refinement chat.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `NOT_STARTED`                  |
| Owner         | —                              |
| Last Updated  | —                              |

### Dependencies

| Work State File            | Required Status    | Notes                                    |
|----------------------------|--------------------|------------------------------------------|
| `00_infrastructure.md`     | `DONE`             | Next.js scaffold must exist              |
| `03_backend_api.md`        | `IN_PROGRESS`      | Need endpoint contracts defined, not necessarily running |

---

## Objective

Build a polished, monday.com-inspired React UI that lets a CSM select a customer account, trigger QBR generation with a real-time streaming view of the agent's thought process, review and edit the generated Markdown, and refine it via natural language chat. The UX should feel like a co-pilot, not a black box.

---

## Plan

### Layout & Styling Foundation
- [ ] Configure Tailwind with a monday.com-inspired color palette (primary purple/blue, clean whites, soft grays)
- [ ] Set up a root layout in `frontend/app/layout.tsx` with a top nav bar ("QBR Co-Pilot" branding) and a main content area
- [ ] Create shared UI components in `frontend/components/ui/`:
  - `Card` — container with shadow and rounded corners
  - `Button` — primary/secondary variants
  - `Badge` — for status indicators (health, risk level)
  - `Spinner` — loading indicator

### Account Selector (The Command Center)
- [ ] Create `frontend/app/page.tsx` as the account selector dashboard
- [ ] Fetch accounts from `GET /api/accounts` on mount
- [ ] Display accounts as clickable cards in a grid, each showing:
  - Account name, plan type badge
  - Key metrics: active users, NPS, SCAT score, risk score
  - Color-coded risk indicator (green/yellow/red based on `risk_engine_score`)
- [ ] Clicking an account navigates to `/account/[name]`

### Account Detail & QBR Generation
- [ ] Create `frontend/app/account/[name]/page.tsx`
- [ ] Display the **Account Snapshot** panel:
  - Structured data in a clean table/card layout (all 13 fields, grouped logically)
  - Quantitative metrics with visual indicators (progress bars for adoption, trend arrows for growth)
  - Qualitative data (CRM notes, feedback) in a styled text block
- [ ] Add a prominent **"Draft QBR"** button
- [ ] On click, connect to `POST /api/generate-qbr` via AG-UI protocol (using CopilotKit's `useCoAgentStateRender` hook or AG-UI `HttpAgent` client):
  - Show a **Thought Process Panel** that displays streaming stages based on AG-UI events:
    - `STEP_STARTED` events trigger an animated indicator with the step name (e.g., "Analyzing usage metrics and QoQ growth...")
    - `STATE_DELTA` events display intermediate insight cards (quant results, qual results) as they arrive
    - `STEP_FINISHED` events mark each stage with a checkmark
  - When the `RUN_FINISHED` event arrives, transition to the editor view

### Interactive QBR Editor (HITL)
- [ ] Create `frontend/components/QBREditor.tsx`:
  - Render the generated Markdown draft using `react-markdown`
  - Provide a toggle between "Preview" and "Edit" modes
  - In Edit mode, show a textarea/code editor with the raw Markdown
  - Edits update the local draft state in real time
- [ ] Add a **Refine Chat Input** below the editor:
  - A text input + "Refine" button
  - Sends `POST /api/refine-qbr` with current draft and the user's instruction
  - Replaces the current draft with the refined version
  - Shows a loading state while refining
- [ ] Add an **"Export"** button that copies the final Markdown to clipboard or downloads as `.md`

### API Integration
- [ ] Set up CopilotKit provider in `frontend/app/layout.tsx` wrapping the app with `<CopilotKit>` and configuring the backend URL
- [ ] Create an API client module at `frontend/lib/api.ts`:
  - `fetchAccounts(): Promise<Account[]>` (plain REST call)
  - `generateQBR(accountName: string)`: use AG-UI `HttpAgent` client or CopilotKit's `useCoAgentStateRender` hook to connect to the AG-UI SSE endpoint and receive typed events
  - `refineQBR(draft: string, instructions: string): Promise<string>` (plain REST call)
  - Base URL configured via `NEXT_PUBLIC_API_URL` env var (defaults to `http://localhost:8000`)
- [ ] Define TypeScript types in `frontend/lib/types.ts` mirroring the backend models and AG-UI event payloads

### Polish & Edge Cases
- [ ] Handle API errors gracefully (show error messages, retry buttons)
- [ ] Add loading skeletons for the account list and snapshot
- [ ] Responsive layout (works on laptop screens, no mobile required for PoC)
- [ ] Add favicon and page titles

---

## Acceptance Criteria

- [ ] Homepage displays 5 account cards with key metrics and risk indicators
- [ ] Clicking an account shows the full account snapshot with all 13 fields
- [ ] Clicking "Draft QBR" streams AG-UI lifecycle events in real time with animated indicators per step
- [ ] Generated Markdown is displayed in a readable preview
- [ ] Toggling to Edit mode shows raw Markdown in a textarea
- [ ] Typing a refinement instruction and clicking "Refine" updates the draft
- [ ] Export button copies Markdown to clipboard
- [ ] API errors show user-friendly error messages
- [ ] UI is visually polished with a monday.com-inspired look

---

## Technical Decisions

_No decisions yet._

---

## Dependencies Detail

### `00_infrastructure.md`

- **What is needed:** A scaffolded Next.js project with TypeScript and Tailwind CSS configured.
- **Expected interface/contract:** `npm run dev` starts the dev server on `http://localhost:3000`. Tailwind classes work out of the box. App Router (`app/` directory) is the routing convention.

### `03_backend_api.md`

- **What is needed:** The API endpoint contracts (request/response schemas, AG-UI event format). The actual backend does not need to be running for initial frontend development — mock data can be used.
- **Expected interface/contract:**
  - `GET /api/accounts` -> `Account[]` (13-field objects)
  - `POST /api/generate-qbr` -> AG-UI SSE stream with standard event types:
    - `RUN_STARTED` / `RUN_FINISHED` — lifecycle boundaries
    - `STEP_STARTED` / `STEP_FINISHED` — per-node progress (quant_agent, qual_agent, strategist, editor)
    - `STATE_DELTA` — intermediate insights (`quantitative_insights`, `qualitative_insights`, `strategic_synthesis`)
    - `TEXT_MESSAGE_CONTENT` — final Markdown draft
  - `POST /api/refine-qbr` -> `{ refined_draft: string }`
- **AG-UI frontend deps:** `@copilotkit/react-core`, `@copilotkit/react-ui` (from `00_infrastructure.md`)

---

## Log

_No entries yet._
