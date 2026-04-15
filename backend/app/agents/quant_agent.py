"""Quantitative analysis node for the QBR workflow."""

from app.agents.llm import AGENT_MODEL_CONFIG, invoke_structured_output
from app.agents.schemas import QuantInsights
from app.agents.state import WorkflowState, ensure_account
from app.prompt_templates.quant import QUANT_SYSTEM_PROMPT, render_quant_user_prompt


def generate_quantitative_insights(account) -> QuantInsights:
    """Generate structured quantitative insights for an account."""

    user_prompt = render_quant_user_prompt(
        account_name=account.account_name,
        plan_type=account.plan_type,
        active_users=account.active_users,
        usage_growth_qoq=f"{account.usage_growth_qoq:.2%}",
        automation_adoption_pct=f"{account.automation_adoption_pct:.2%}",
        tickets_last_quarter=account.tickets_last_quarter,
        avg_response_time=f"{account.avg_response_time:.1f}",
        nps_score=f"{account.nps_score:.1f}",
        preferred_channel=account.preferred_channel,
        scat_score=f"{account.scat_score:.1f}",
        risk_engine_score=f"{account.risk_engine_score:.2f}",
    )
    return invoke_structured_output(
        system_prompt=QUANT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=QuantInsights,
        model=AGENT_MODEL_CONFIG["extractor"],
    )


def run_quant_agent(state: WorkflowState) -> dict[str, dict]:
    """LangGraph node that adds quantitative insights to the workflow state."""

    account = ensure_account(state["account"])
    insights = generate_quantitative_insights(account)
    return {"quantitative_insights": insights.model_dump()}
