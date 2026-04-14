# Infrastructure Setup

> Initialize the repository, package managers, monorepo structure, and all foundational config files.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `NOT_STARTED`                  |
| Owner         | —                              |
| Last Updated  | —                              |

### Dependencies

_None — this is the root workstream._

---

## Objective

Stand up the full project skeleton so that every downstream workstream (data layer, agents, API, frontend, deployment) can begin work in a clean, reproducible environment. When done, a developer (or agent) can clone the repo, run one setup command per side (Python backend, Node frontend), and have a working dev loop.

---

## Plan

- [ ] Initialize a git repository at the project root (`/Users/yankri/Documents/Monday`)
- [ ] Create the monorepo directory structure:
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
- [ ] Set up Python backend with `uv`:
  - Create `backend/pyproject.toml` with project metadata and core dependencies:
    - `fastapi`, `uvicorn`, `pydantic`, `langchain`, `langgraph`, `langchain-openai`, `openpyxl`, `python-dotenv`
    - `ag-ui-protocol`, `ag-ui-langgraph` (AG-UI streaming protocol for LangGraph)
  - Run `uv sync` inside `backend/` to create the virtual environment and lock file
- [ ] Scaffold the Next.js frontend:
  - Run `npx create-next-app@latest frontend` with TypeScript, Tailwind CSS, App Router enabled
  - Install AG-UI frontend dependencies: `@copilotkit/react-core`, `@copilotkit/react-ui` (CopilotKit provides AG-UI React hooks for agent state rendering)
  - Verify `npm run dev` starts the dev server on port 3000
- [ ] Create project-level config files:
  - `.gitignore` — Python venvs, `node_modules`, `.env`, `__pycache__`, `.next`, etc.
  - `.env.example` — document required env vars (`OPENAI_API_KEY`)
  - Root `README.md` — project overview, setup instructions, tech stack summary
- [ ] Make the initial git commit with the full scaffold

---

## Acceptance Criteria

- [ ] `git log` shows at least one commit
- [ ] `cd backend && uv run python -c "print('ok')"` exits 0 and prints `ok`
- [ ] `cd backend && uv run python -c "from ag_ui_langgraph import add_langgraph_fastapi_endpoint; print('ok')"` succeeds
- [ ] `cd frontend && npm run dev` starts Next.js dev server without errors
- [ ] `.gitignore` correctly excludes `node_modules/`, `.env`, `__pycache__/`, `.next/`
- [ ] `.env.example` exists with `OPENAI_API_KEY=` placeholder
- [ ] Directory structure matches the plan above

---

## Technical Decisions

_No decisions yet._

---

## Dependencies Detail

_No dependencies — this is the root workstream._

---

## Log

_No entries yet._
