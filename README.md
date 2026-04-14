# monday.com QBR Co-Pilot

An intelligent agent infrastructure for Customer Success Managers — a human-in-the-loop QBR (Quarterly Business Review) Co-Pilot that automates data analysis and generates evidence-grounded presentation drafts.

## Tech Stack

| Layer            | Technology                                         |
| ---------------- | -------------------------------------------------- |
| Frontend         | Next.js, React, Tailwind CSS, CopilotKit (AG-UI)  |
| Backend          | FastAPI, Uvicorn, Pydantic                         |
| Agent Framework  | LangGraph, LangChain                               |
| Streaming        | AG-UI Protocol (`ag-ui-langgraph`)                 |
| LLM              | OpenAI                                             |

## Project Structure

```
Monday/
├── backend/          # FastAPI + LangGraph agent backend
│   ├── app/          # Application code
│   └── pyproject.toml
├── frontend/         # Next.js App Router frontend
├── docs/             # Architecture & planning docs
└── work_states/      # Workstream tracking
```

## Setup

### Prerequisites

- [Homebrew](https://brew.sh/)
- [uv](https://docs.astral.sh/uv/) (`brew install uv`)
- [Node.js](https://nodejs.org/) (`brew install node`)

### Backend

```bash
cd backend
uv sync          # creates .venv and installs all dependencies
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # starts dev server on http://localhost:3000
```

### Environment Variables

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

| Variable         | Description           |
| ---------------- | --------------------- |
| `OPENAI_API_KEY` | OpenAI API secret key |
