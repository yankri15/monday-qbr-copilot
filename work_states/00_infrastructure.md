# Infrastructure Setup

> Initialize the repository, package managers, monorepo structure, and all foundational config files.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | Agent                          |
| Last Updated  | 2026-04-14                     |

### Dependencies

_None — this is the root workstream._

---

## Objective

Stand up the full project skeleton so that every downstream workstream (data layer, agents, API, frontend, deployment) can begin work in a clean, reproducible environment. When done, a developer (or agent) can clone the repo, run one setup command per side (Python backend, Node frontend), and have a working dev loop.

---

## Plan

- [x] Initialize a git repository at the project root (`/Users/yankri/Documents/Monday`)
- [x] Create the monorepo directory structure:
  ```
  backend/
    app/
      __init__.py
    pyproject.toml
  frontend/
    (Next.js scaffold — created via create-next-app)
  docs/           (already exists)
  work_states/    (already exists)
  ```
- [x] Set up Python backend with `uv`:
  - Create `backend/pyproject.toml` with project metadata and core dependencies:
    - `fastapi`, `uvicorn`, `pydantic`, `langchain`, `langgraph`, `langchain-openai`, `openpyxl`, `python-dotenv`
    - `ag-ui-protocol`, `ag-ui-langgraph` (AG-UI streaming protocol for LangGraph)
  - Run `uv sync` inside `backend/` to create the virtual environment and lock file
- [x] Scaffold the Next.js frontend:
  - Run `npx create-next-app@latest frontend` with TypeScript, Tailwind CSS, App Router enabled
  - Install AG-UI frontend dependencies: `@copilotkit/react-core`, `@copilotkit/react-ui` (CopilotKit provides AG-UI React hooks for agent state rendering)
  - Verify `npm run dev` starts the dev server on port 3000
- [x] Create project-level config files:
  - `.gitignore` — Python venvs, `node_modules`, `.env`, `__pycache__`, `.next`, etc.
  - `.env.example` — document required env vars (`OPENAI_API_KEY`)
  - Root `README.md` — project overview, setup instructions, tech stack summary
- [x] Make the initial git commit with the full scaffold

---

## Acceptance Criteria

- [x] `git log` shows at least one commit
- [x] `cd backend && uv run python -c "print('ok')"` exits 0 and prints `ok`
- [x] `cd backend && uv run python -c "from ag_ui_langgraph import add_langgraph_fastapi_endpoint; print('ok')"` succeeds
- [x] `cd frontend && npm run dev` starts Next.js dev server without errors
- [x] `.gitignore` correctly excludes `node_modules/`, `.env`, `__pycache__/`, `.next/`
- [x] `.env.example` exists with `OPENAI_API_KEY=` placeholder
- [x] Directory structure matches the plan above

---

## Technical Decisions

- **Python 3.12** via `uv python install 3.12` (system Python 3.9.6 is too old for FastAPI/LangGraph)
- **uv** for dependency management — creates `.venv/` inside `backend/`, lockfile at `backend/uv.lock`
- **Hatchling** as the build backend with explicit `packages = ["app"]` in `pyproject.toml`
- **Next.js 16** (v16.2.3) with Turbopack, App Router, `src/` directory layout
- **npm** as the frontend package manager (not yarn/pnpm)

---

## Dependencies Detail

_No dependencies — this is the root workstream._

---

## Log

- **2026-04-14** — Installed `uv` (0.11.6) and `node` (v25.9.0) via Homebrew.
- **2026-04-14** — Initialized git repo, created `.gitignore`.
- **2026-04-14** — Scaffolded `backend/` with `pyproject.toml`; installed Python 3.12.13 and 51 packages via `uv sync`.
- **2026-04-14** — Scaffolded `frontend/` via `create-next-app` (Next.js 16.2.3); installed `@copilotkit/react-core` and `@copilotkit/react-ui`.
- **2026-04-14** — Created `.env.example` and root `README.md`.
- **2026-04-14** — Initial commit `527c7b1` on `main`. All acceptance criteria verified.
