# Frontend (Next.js)

> Build the QBR Co-Pilot UI: account selector, streaming generation view, interactive Markdown editor, and refinement chat.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | `Codex`                        |
| Last Updated  | `2026-04-15`                   |

### Dependencies

| Work State File            | Required Status    | Notes                                    |
|----------------------------|--------------------|------------------------------------------|
| `00_infrastructure.md`     | `DONE`             | Next.js scaffold must exist              |
| `03_backend_api.md`        | `DONE`             | Backend routes and AG-UI event stream implemented |

---

## Objective

Build a polished, monday.com-inspired React UI that lets a CSM select a customer account, trigger QBR generation with a real-time streaming view of the agent's thought process, review and edit the generated Markdown, and refine it via natural language chat. The UX should feel like a co-pilot, not a black box.

---

## Plan

### Layout & Styling Foundation
- [x] Configure Tailwind with a monday.com-inspired color palette (primary purple/blue, clean whites, soft grays)
- [x] Set up a root layout in `frontend/app/layout.tsx` with a top nav bar ("QBR Co-Pilot" branding) and a main content area
- [x] Create shared UI components in `frontend/components/ui/`:
  - `Card` — container with shadow and rounded corners
  - `Button` — primary/secondary variants
  - `Badge` — for status indicators (health, risk level)
  - `Spinner` — loading indicator

### Account Selector (The Command Center)
- [x] Create `frontend/app/page.tsx` as the account selector dashboard
- [x] Fetch accounts from `GET /api/accounts` on mount
- [x] Display accounts as clickable cards in a grid, each showing:
  - Account name, plan type badge
  - Key metrics: active users, NPS, SCAT score, risk score
  - Color-coded risk indicator (green/yellow/red based on `risk_engine_score`)
- [x] Clicking an account navigates to `/account/[name]`

### Account Detail & QBR Generation
- [x] Create `frontend/app/account/[name]/page.tsx`
- [x] Display the **Account Snapshot** panel:
  - Structured data in a clean table/card layout (all 13 fields, grouped logically)
  - Quantitative metrics with visual indicators (progress bars for adoption, trend arrows for growth)
  - Qualitative data (CRM notes, feedback) in a styled text block
- [x] Add a prominent **"Draft QBR"** button
- [x] On click, connect to `POST /api/generate-qbr` via AG-UI protocol (implemented with a custom SSE client rather than CopilotKit runtime hooks):
  - Show a **Thought Process Panel** that displays streaming stages based on AG-UI events:
    - `STEP_STARTED` events trigger an animated indicator with the step name (e.g., "Analyzing usage metrics and QoQ growth...")
    - `STATE_DELTA` events display intermediate insight cards (quant results, qual results) as they arrive
    - `STEP_FINISHED` events mark each stage with a checkmark
  - When the `RUN_FINISHED` event arrives, transition to the editor view

### Interactive QBR Editor (HITL)
- [x] Create `frontend/components/QBREditor.tsx`:
  - Render the generated Markdown draft using `react-markdown`
  - Provide a toggle between "Preview" and "Edit" modes
  - In Edit mode, show a textarea/code editor with the raw Markdown
  - Edits update the local draft state in real time
- [x] Add a **Refine Chat Input** below the editor:
  - A text input + "Refine" button
  - Sends `POST /api/refine-qbr` with current draft and the user's instruction
  - Replaces the current draft with the refined version
  - Shows a loading state while refining
- [x] Add an **"Export"** button that copies the final Markdown to clipboard or downloads as `.md`

### API Integration
- [x] Attempt CopilotKit provider integration and document the fallback decision
- [x] Create an API client module at `frontend/lib/api.ts`:
  - `fetchAccounts(): Promise<Account[]>` (plain REST call)
  - `generateQBR(accountName: string)`: implemented as a lightweight typed SSE client for the AG-UI event stream
  - `refineQBR(draft: string, instructions: string): Promise<string>` (plain REST call)
  - Base URL configured via `NEXT_PUBLIC_API_URL` env var and falls back to the current browser hostname on port `8000`
- [x] Define TypeScript types in `frontend/lib/types.ts` mirroring the backend models and AG-UI event payloads

### Polish & Edge Cases
- [x] Handle API errors gracefully (show error messages, retry buttons)
- [x] Add loading skeletons for the account list and snapshot
- [x] Responsive layout (works on laptop screens, no mobile required for PoC)
- [x] Add favicon and page titles

---

## Acceptance Criteria

- [x] Homepage displays 5 account cards with key metrics and risk indicators
- [x] Clicking an account shows the full account snapshot with all 13 fields
- [x] Clicking "Draft QBR" streams AG-UI lifecycle events in real time with animated indicators per step
- [x] Generated Markdown is displayed in a readable preview
- [x] Toggling to Edit mode shows raw Markdown in a textarea
- [x] Typing a refinement instruction and clicking "Refine" updates the draft
- [x] Export button copies Markdown to clipboard
- [x] API errors show user-friendly error messages
- [x] UI is visually polished with a monday.com-inspired look

---

## Technical Decisions

- CopilotKit was scaffolded and a `CopilotProvider` component was created, but the active provider mount was removed from `frontend/src/app/layout.tsx`. In this repo, the CopilotKit runtime path introduced a frontend build/runtime incompatibility tied to the current Next.js 16 + Turbopack setup and CSS processing, so the UI now talks to the backend AG-UI SSE endpoint through a custom typed client in `frontend/src/lib/api.ts`.
- The frontend API base URL no longer hardcodes `localhost`. When `NEXT_PUBLIC_API_URL` is not set, the client derives the current browser hostname and targets port `8000`, which avoids `localhost` versus `127.0.0.1` CORS mismatches during local verification.
- Google-hosted fonts were not used because build-time font fetching is unreliable in the current environment. The UI uses local/system font stacks instead, preserving the visual direction without introducing another external dependency.
- `npm run build` is not treated as a clean sign-off in this environment yet. Next.js 16's default Turbopack production build currently fails with an internal error while processing `src/app/globals.css`, specifically when Turbopack tries to create a new process and bind to a port. The application is verified through `next dev --webpack`, linting, backend integration, and real browser testing instead.

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

- `2026-04-15` Built the account selector dashboard, account detail route, snapshot panels, streaming thought-process panel, and interactive markdown editor.
- `2026-04-15` Implemented frontend API integration in `frontend/src/lib/api.ts` for accounts, AG-UI SSE generation, and draft refinement.
- `2026-04-15` Added user-facing error states, loading states, page metadata, and responsive polish across the QBR workspace.
- `2026-04-15` Attempted CopilotKit runtime/provider integration, hit a compatibility issue in the current Next.js 16/Turbopack setup, and intentionally switched the active implementation to a custom AG-UI SSE client while keeping the codebase ready to revisit CopilotKit later.
- `2026-04-15` Verified the end-to-end browser flow for homepage -> account detail -> Draft QBR -> live AG-UI updates -> refined draft -> clipboard export.
- `2026-04-15` Re-ran `npm run build`; it still fails under Turbopack with `Failed to write app endpoint /page` caused by `src/app/globals.css` attempting to create a new process and bind to a port (`Operation not permitted`).
