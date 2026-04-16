# monday.com QBR Co-Pilot

A submission-ready proof of concept for a Customer Success QBR workflow built around a multi-step AI pipeline.

The product helps a CSM generate a strong first-draft Quarterly Business Review from structured account metrics and qualitative CRM context, while keeping the reasoning visible and the final output editable by a human.

## What It Does

- Generates a QBR draft for a selected customer account
- Separates structured and unstructured analysis into dedicated workflow steps
- Produces evidence-grounded recommendations and a polished final draft
- Streams intermediate workflow progress to the UI
- Supports CSV / XLSX uploads for demo account data
- Exports the final draft as Markdown or PDF

## Workflow

The backend uses a LangGraph workflow with specialized steps:

1. `quant_agent`
   Interprets structured account metrics into a compact business readout.
2. `qual_agent`
   Extracts sentiment, themes, and action signals from CRM notes and feedback.
3. `strategist`
   Combines the quantitative and qualitative views into a strategic synthesis.
4. `csm_judge`
   Reviews the synthesis for grounding, actionability, and product-language quality.
5. `editor`
   Converts the approved synthesis into the final QBR draft.

## Tech Stack

- Frontend: Next.js, React, Tailwind CSS, CopilotKit
- Backend: FastAPI, Pydantic
- Workflow orchestration: LangGraph, LangChain
- LLM provider: OpenAI
- Deployment: Vercel

## Project Structure

```text
backend/
  app/
    agents/
    data/
    models/
    prompt_templates/
    routes/
    services/
  data/
  tests/

frontend/
  src/
    app/
    components/
    lib/
```

## Local Setup

### Prerequisites

- Node.js
- `uv`
- OpenAI API key

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3001
```

### Environment

Create a root `.env` file with:

```bash
OPENAI_API_KEY=your_key_here
```

## Deployment

The project is configured as a single Vercel project using `experimentalServices`:

- frontend served from `/`
- FastAPI backend served from `/api`

Current production URL:

- [monday-qbr-copilot.vercel.app](https://monday-qbr-copilot.vercel.app)

## Estimated LLM Cost

With the current default model routing:

- `gpt-4.1-mini` for `quant_agent` and `qual_agent`
- `gpt-4.1` for `strategist`, `csm_judge`, and `editor`

the estimated cost of a single QBR draft generation is roughly `$0.02–$0.03` per run.

This estimate is based on the current prompt sizes and a real production-style Altura Systems generation. Actual cost will vary slightly based on account data size, output length, and whether the judge step triggers a retry of the strategist.

## Notes

- The sample account dataset lives in `backend/data/sample_customers_q3_2025.xlsx`.
- The submission repository intentionally excludes internal planning docs, generated deliverables, and local working artifacts.
