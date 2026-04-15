"""Editorial node for formatting the final QBR markdown draft."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_text_output
from app.agents.schemas import StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account

EDITOR_SYSTEM_PROMPT = """
You are the Editor Agent for a monday.com Customer Success QBR co-pilot.
Turn the strategic synthesis into a polished Markdown draft that reads like a real CSM narrative, not a bullet dump.

Instructions:
- Use monday.com product language throughout: Boards, Automations, Integrations, Workspaces, Dashboards, Work OS.
- Keep the writing evidence-grounded, specific, and presentation-ready.
- Adapt to the requested audience tone:
  - executive: high-level strategic language, minimal technical detail, focus on business impact and ROI.
  - team_lead: operational language, workflow-specific recommendations, mention concrete Boards and Automations.
  - technical: include implementation considerations such as Integrations, APIs, data flow, and Automation logic.
- Ensure the Next Steps section contains calendar-ready actions with suggested owners and timelines.
- If source context references named external vendors or tools, convert them into monday-first language such as integration workflows, connected systems, or development workflow support. Do not let third-party brand names dominate the final draft.
- Do not mention that an AI wrote the draft.
""".strip()


def generate_final_draft(
    account,
    strategic_synthesis: StrategicSynthesis,
    *,
    tone: str = "executive",
) -> str:
    """Generate the final markdown QBR draft."""

    user_prompt = f"""
Create a slide-ready QBR draft in Markdown for this customer.

Account context:
- Account name: {account.account_name}
- Plan type: {account.plan_type}
- Preferred channel: {account.preferred_channel}
- Active users: {account.active_users}
- Usage growth QoQ: {account.usage_growth_qoq:.2%}
- Automation adoption: {account.automation_adoption_pct:.2%}
- Support tickets last quarter: {account.tickets_last_quarter}
- Avg response time: {account.avg_response_time:.1f} hours
- NPS score: {account.nps_score:.1f}
- SCAT score: {account.scat_score:.1f}
- Risk engine score: {account.risk_engine_score:.2f}
- Audience tone: {tone}

Strategic synthesis:
{strategic_synthesis.model_dump_json(indent=2)}

Format with exactly these sections:
# {account.account_name} QBR Draft
## Executive Summary
## Key Metrics
## Health Assessment
## Recommendations
## Next Steps

Include concrete evidence and keep each section concise.
""".strip()
    draft = invoke_text_output(
        system_prompt=EDITOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        model=AGENT_MODEL_CONFIG["thinker"],
    )
    return normalize_monday_facing_language(draft)


def run_editor(state: WorkflowState) -> dict[str, str]:
    """LangGraph node that formats the final markdown draft."""

    account = ensure_account(state["account"])
    strategic_synthesis = StrategicSynthesis.model_validate(state["strategic_synthesis"])
    draft = generate_final_draft(
        account,
        strategic_synthesis,
        tone=state.get("tone", "executive"),
    )
    return {"final_draft": draft}
