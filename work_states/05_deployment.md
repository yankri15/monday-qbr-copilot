# Deployment (Vercel)

> Configure Vercel deployment for the monorepo, wire environment variables, and perform final integration testing.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | `Codex`                        |
| Last Updated  | `2026-04-15`                   |

### Dependencies

| Work State File            | Required Status |
|----------------------------|-----------------|
| `03_backend_api.md`        | `DONE`          |
| `04_frontend.md`           | `DONE`          |

---

## Objective

Deploy the complete QBR Co-Pilot application to Vercel so it is publicly accessible via a URL. The Next.js frontend and FastAPI backend must both be hosted and communicating correctly. The deployment should be reproducible and environment variables securely managed.

---

## Plan

- [x] Evaluate deployment strategy for FastAPI on Vercel:
  - [x] Option A chosen: use a single Vercel project with `experimentalServices`, keeping `frontend/` as the Next.js service and exposing the FastAPI backend as a Python service at `/api`
  - [ ] Option B not selected: deploy FastAPI separately (e.g., Railway, Render, Fly.io) and point the Vercel frontend at it
  - [x] Document the chosen approach as a Technical Decision
- [x] Configure Vercel project settings:
  - [x] Use root `vercel.json` service config instead of a `frontend/` root-directory-only deploy
  - [x] Configure frontend build command as `npm run build` (`next build --webpack`)
  - [x] Verify the frontend production output builds successfully on Vercel
- [x] If using Vercel Serverless for backend:
  - [x] Add a Vercel Python entrypoint at `backend/main.py`
  - [x] Add a root `vercel.json` with `experimentalServices` routing `/` to `frontend/` and `/api` to the Python service
  - [x] Confirm the backend dependency set is installed through `backend/uv.lock` / `backend/pyproject.toml`
- [ ] If using external backend hosting:
  - Deploy FastAPI to the chosen platform
  - Update `NEXT_PUBLIC_API_URL` in Vercel environment variables to point to the backend URL
- [x] Configure environment variables in Vercel dashboard:
  - [x] `OPENAI_API_KEY` — configured in Vercel production env
  - [x] `NEXT_PUBLIC_API_URL` — not needed for the chosen same-origin services setup
- [x] Deploy and test:
  - [x] Deploy to Vercel production through the CLI-linked project
  - [x] Verify the frontend loads at the Vercel URL
  - [x] Verify `GET /api/accounts` returns data
  - [x] Verify the full QBR generation flow works end-to-end
  - [x] Verify the refinement flow works
- [x] Final smoke test checklist:
  - [x] Account selector loads all 5 accounts
  - [x] Clicking an account routes to the account workspace
  - [x] "Draft QBR" streams thought process and produces a draft
  - [x] Editing the draft works in the editor
  - [x] Refining via chat input returns an updated draft
  - [x] No console errors, no CORS issues in the deployed smoke pass
- [x] Document the deployed URL in the root README.md

---

## Acceptance Criteria

- [x] The application is accessible at a public Vercel URL
- [x] The full QBR generation flow works end-to-end from the deployed URL (select account -> generate -> review -> refine)
- [x] Environment variables are securely configured (not committed to the repo)
- [x] The deployment is reproducible from a clean CLI deploy (`npx vercel deploy --prod`) against the linked Vercel project
- [x] README.md contains the live deployment URL and any access instructions

---

## Technical Decisions

- [DECISION] 2026-04-15: Deploy as a single Vercel project using `experimentalServices`, with `frontend/` served at `/` and a Vercel-specific FastAPI entrypoint served at `/api`. — Rationale: this keeps the public demo on one domain, avoids cross-origin complexity, and matches the “complete app on Vercel” goal in the work state.
- [DECISION] 2026-04-15: Force frontend production builds through Webpack by setting `npm run build` to `next build --webpack`. — Rationale: the current environment consistently hits a Turbopack CSS-worker panic, while the Webpack production build completes successfully.
- [DECISION] 2026-04-15: Pass the selected account payload in the QBR generation request so uploaded accounts remain usable in stateless/serverless environments. — Rationale: the current upload store is in-memory and therefore not reliable across separate serverless invocations during deployment.
- [DECISION] 2026-04-15: Complete the POC deployment through a Vercel CLI-linked project rather than requiring GitHub integration first. — Rationale: the recruiter demo needs a stable public URL quickly, and GitHub-triggered auto-deploys can be added later without changing the runtime architecture.
- [DECISION] 2026-04-15: Route deployed QBR generation through a deployment-safe manual SSE adapter and normalize the frontend account payload before validation. — Rationale: Vercel production requests include UI-only account metadata (`account_source`, `upload_id`), and the manual SSE path is the most reliable way to preserve the co-pilot event stream shape on the serverless deployment.

---

## Dependencies Detail

### `03_backend_api.md`

- **What is needed:** A fully working FastAPI application with all 3 endpoints tested locally.
- **Expected interface/contract:** Running `uv run uvicorn app.main:app` in `backend/` serves the API on port 8000. All endpoints (`/api/health`, `/api/accounts`, `/api/generate-qbr`, `/api/refine-qbr`) respond correctly.

### `04_frontend.md`

- **What is needed:** A fully working Next.js application that consumes the backend API.
- **Expected interface/contract:** Running `npm run build` in `frontend/` produces a production build without errors. The app correctly reads `NEXT_PUBLIC_API_URL` for backend communication.

---

## Log

- [START] 2026-04-15: Began `05_deployment` by reviewing the work state, checking the repo for existing Vercel linkage/config, and validating the current local deploy shape.
- [PROGRESS] 2026-04-15: Verified that the default Next 16 Turbopack production build still fails in this environment, while `next build --webpack` succeeds, making a Webpack-based frontend deploy path viable.
- [PROGRESS] 2026-04-15: Chose a single-project Vercel deployment strategy using `experimentalServices`, added a Vercel-specific FastAPI entrypoint plus root `vercel.json`, and switched the frontend API base to same-origin production routing.
- [PROGRESS] 2026-04-15: Hardened QBR generation for uploaded accounts by allowing the frontend to send the selected account payload directly, avoiding reliance on in-memory upload state during deployment.
- [PROGRESS] 2026-04-15: Linked the repo to the Vercel project `monday-qbr-copilot`, configured the production `OPENAI_API_KEY`, and deployed the app publicly at `https://monday-qbr-copilot.vercel.app`.
- [PROGRESS] 2026-04-15: Fixed production `generate-qbr` failures by selecting the deployment-safe stream path based on deployed host signals and stripping UI-only fields from the client-sent account payload before validating it into `CustomerAccount`.
- [VERIFY] 2026-04-15: Verified the live alias end to end: `GET /api/health` returns `{"status":"ok"}`, `GET /api/accounts` returns all 5 sample accounts, `POST /api/refine-qbr` returns a refined draft, and `POST /api/generate-qbr` streams `RUN_STARTED`, step events, state deltas, draft text, and `RUN_FINISHED`.
- [VERIFY] 2026-04-15: Performed a browser smoke pass on the deployed URL: homepage loaded, 5 account cards rendered, account routing opened `Altura Systems`, and the console reported `0` errors / `0` warnings.
- [DONE] 2026-04-15: `05_deployment` complete for the chosen Vercel CLI deployment path.
