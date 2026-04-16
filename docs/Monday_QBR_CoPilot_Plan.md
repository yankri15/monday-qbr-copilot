# 🚀 monday.com AI Innovation Builder: QBR Co-Pilot Architecture Plan

## 1. The Product Vision: Human-in-the-Loop (HITL) QBR Co-Pilot
Instead of a simple script that outputs a static text block, this solution is an **intelligent agent infrastructure** designed specifically for Customer Success Managers (CSMs). It transitions the AI from a basic text generator to an active "Co-Pilot" that does the heavy analytical lifting while leaving the final strategic sign-off to the human.

### Key Product Principles:
* **Trust through Transparency:** The system explicitly cites *why* a recommendation is made (e.g., grounding a cross-sell suggestion in the 85% automation adoption rate and positive CRM notes).
* **Actionable Outputs:** The final generation is not just a summary, but a structured presentation outline with concrete next steps.
* **Frictionless UX:** Reduces the 5+ hours of manual data-mining into a 15-minute review and refine session.

---

## 2. Tech Stack & Deployment Strategy
To demonstrate full end-to-end (e2e) product ownership and deliver a production-ready feel:
* **Frontend:** Next.js / React (Tailwind CSS for sleek, monday-esque UI) + CopilotKit for agent-UI integration.
* **Backend:** FastAPI (Python) - lightweight, fast, and native to AI libraries.
* **Agent Framework:** LangGraph for explicit, modular state management.
* **Agent-User Streaming:** AG-UI Protocol (`ag-ui-langgraph`) — the open standard for agent-to-frontend communication via SSE, providing lifecycle events, state sync, and structured streaming.
* **Deployment:** Vercel (Monorepo hosting both the Next.js FE and FastAPI serverless functions).
* **LLM Provider:** OpenAI API key

---

## 3. The UX/UI: The "Co-Pilot" Experience (Frontend)
The interface is designed to make the CSM feel empowered, not replaced.

* **The Command Center:** A dashboard where the CSM selects an account. The UI fetches and displays a clean "Account Snapshot" of raw structured (active users, SCAT score) and unstructured (CRM notes, feedback) data.
* **Agentic UI Streaming (The "Shock Factor"):** When "Draft QBR" is clicked, the UI utilizes AG-UI Protocol over SSE to stream the agent's thought process in real-time:
  * ⏳ *Analyzing usage metrics and QoQ growth...*
  * ⏳ *Extracting sentiment from CRM notes...*
  * ⏳ *Synthesizing next-step recommendations...*
* **Interactive Review (HITL):** The output is presented in editable Markdown. The CSM can manually tweak the text or use a "Refine" chat input (e.g., *"Make the tone more optimistic"* or *"Focus more on the active user growth"*).

---

## 4. The Backend Architecture (FastAPI)
A lean, modular API layer connecting the UI to the AI reasoning engine.

### Core Endpoints:
* `GET /api/accounts`: Returns the simulated customer dataset.
* `POST /api/generate-qbr`: The primary orchestrator. Takes an `account_name`, triggers the LangGraph workflow, and streams back AG-UI events (lifecycle, state deltas, final Markdown).
* `POST /api/refine-qbr`: Accepts the current QBR draft and natural language user instructions to return a dynamically refined version.

---

## 5. The Agentic Framework (LangGraph)
By implementing a state graph, we avoid the pitfalls of monolithic prompts (hallucinations, mixed context) and perfectly set up the required "Flow Architecture Diagram" deliverable.

**Workflow State:** Tracks `account` (CustomerAccount input), `quantitative_insights`, `qualitative_insights`, `strategic_synthesis`, and `final_draft`. AG-UI handles lifecycle event streaming natively — no manual thought log needed.

**Key Data Field Definitions (from the assignment dataset):**
* `scat_score` — Success Confidence & Adoption Trend (SCAT), internal health metric (0–100).
* `risk_engine_score` — AI-predicted churn risk (0–1). Higher = greater likelihood of churn.
* `usage_growth_qoq` — % change in usage quarter-over-quarter.
* `automation_adoption_pct` — Automation feature adoption rate.
* `preferred_channel` — Main communication preference (Email / Phone / Chat / In-app chat).

**The Nodes (Sub-Agents):**
1. **Node 1: The Quant Agent:** Ingests structured numeric data (`active_users`, `usage_growth_qoq`, `automation_adoption_pct`, `tickets_last_quarter`, `avg_response_time`, `nps_score`, `scat_score`, `risk_engine_score`) and turns it into a compact business readout. This creates a modular interpretation layer over structured signals and a clean place to absorb richer quantitative inputs later (e.g., `{"health": "at risk", "key_metric": "usage_growth dropped by 10%"}`).
2. **Node 2: The Qual Agent:** Ingests unstructured CRM free text (`crm_notes`, `feedback_summary`). Extracts themes and sentiment using structured JSON outputs (e.g., `{"sentiment": "frustrated", "core_complaint": "slow response times"}`).
3. **Node 3: The Strategist:** Synthesizes the JSON outputs from Node 1 and Node 2, plus `preferred_channel` for communication-aware recommendations. Designed to find the intersection of data and produce evidence-grounded recommendations (e.g., *"Quant shows high churn risk, Qual shows support frustration -> Recommendation: Escalate priority support routing via Chat (preferred channel)."*). Each recommendation cites the specific metrics that support it.
4. **Node 4: The Editor:** Formats the Strategist's synthesized logic into a crisp, slide-ready Markdown narrative with inline data citations.

---

## 6. Alignment with Assignment Deliverables

* **Deliverable 1 (Design Brief):** The Product Vision section perfectly frames the problem, user empathy, and success metrics.
* **Deliverable 2 (Flow Architecture Diagram):** The LangGraph state graph translates directly into a robust system diagram showing data flow, reasoning, and output.
* **Deliverable 3 (Prototype / PoC):** A Vercel-deployed Next.js + FastAPI app is a massive step above a standard Jupyter notebook, showcasing true e2e capability.
* **Deliverable 4 (Prompts & Components Documentation):** Splitting the logic into Quant and Qual agents using Pydantic JSON schemas demonstrates advanced hallucination prevention and structured output handling.
* **Deliverable 6 (Experiment & Reflection):** For "What's next?", we can propose deep integrations like a monday.com automation recipe (e.g., *When status changes to 'QBR Prep', trigger generation and attach to item updates*).
