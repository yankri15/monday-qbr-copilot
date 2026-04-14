# Deployment (Vercel)

> Configure Vercel deployment for the monorepo, wire environment variables, and perform final integration testing.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `NOT_STARTED`                  |
| Owner         | —                              |
| Last Updated  | —                              |

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

- [ ] Evaluate deployment strategy for FastAPI on Vercel:
  - Option A: Vercel Serverless Functions (convert FastAPI routes to serverless handlers via `vercel-python` adapter)
  - Option B: Deploy FastAPI separately (e.g., Railway, Render, Fly.io) and point the Vercel frontend at it
  - Document the chosen approach as a Technical Decision
- [ ] Configure Vercel project settings:
  - Set root directory to `frontend/` for the Next.js build
  - Configure build command: `npm run build`
  - Configure output directory: `.next`
- [ ] If using Vercel Serverless for backend:
  - Create `backend/api/` directory with serverless function wrappers
  - Add a `vercel.json` at the project root with rewrite rules routing `/api/*` to the Python functions
  - Ensure `openpyxl`, `langchain`, `langgraph`, `langchain-openai` are in the serverless function's dependencies
- [ ] If using external backend hosting:
  - Deploy FastAPI to the chosen platform
  - Update `NEXT_PUBLIC_API_URL` in Vercel environment variables to point to the backend URL
- [ ] Configure environment variables in Vercel dashboard:
  - `OPENAI_API_KEY` — required for LLM calls
  - `NEXT_PUBLIC_API_URL` — backend URL (if external)
- [ ] Deploy and test:
  - Push to the connected git branch to trigger Vercel deployment
  - Verify the frontend loads at the Vercel URL
  - Verify `GET /api/accounts` returns data
  - Verify the full QBR generation flow works end-to-end
  - Verify the refinement flow works
- [ ] Final smoke test checklist:
  - [ ] Account selector loads all 5 accounts
  - [ ] Clicking an account shows the snapshot
  - [ ] "Draft QBR" streams thought process and produces a draft
  - [ ] Editing the draft works in the editor
  - [ ] Refining via chat input returns an updated draft
  - [ ] No console errors, no CORS issues
- [ ] Document the deployed URL in the root README.md

---

## Acceptance Criteria

- [ ] The application is accessible at a public Vercel URL
- [ ] The full QBR generation flow works end-to-end from the deployed URL (select account -> generate -> review -> refine)
- [ ] Environment variables are securely configured (not committed to the repo)
- [ ] The deployment is reproducible from a clean git push
- [ ] README.md contains the live deployment URL and any access instructions

---

## Technical Decisions

_No decisions yet._

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

_No entries yet._
