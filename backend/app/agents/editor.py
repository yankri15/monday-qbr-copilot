"""Editorial node for formatting the final QBR markdown draft."""

from app.agents.llm import invoke_text_output
from app.agents.schemas import StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account

EDITOR_SYSTEM_PROMPT = """
You are the Editor Agent for a customer-success QBR copilot.
Turn the strategic synthesis into a crisp, slide-ready Markdown draft.
Use clear section headings and keep the writing executive-friendly, specific, and evidence-grounded.
Do not mention that an AI wrote the draft.
""".strip()


def generate_final_draft(account, strategic_synthesis: StrategicSynthesis) -> str:
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
    return invoke_text_output(
        system_prompt=EDITOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
    )


def run_editor(state: WorkflowState) -> dict[str, str]:
    """LangGraph node that formats the final markdown draft."""

    account = ensure_account(state["account"])
    strategic_synthesis = StrategicSynthesis.model_validate(state["strategic_synthesis"])
    draft = generate_final_draft(account, strategic_synthesis)
    return {"final_draft": draft}
