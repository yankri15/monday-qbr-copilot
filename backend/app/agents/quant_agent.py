"""Quantitative analysis node for the QBR workflow."""

from app.agents.llm import invoke_structured_output
from app.agents.schemas import QuantInsights
from app.agents.state import WorkflowState, ensure_account

QUANT_SYSTEM_PROMPT = """
You are the Quant Agent for a customer-success QBR copilot.
Analyze only the provided structured account metrics.
Return concise, evidence-grounded output. Do not invent values.
Classify health based on growth, adoption, support burden, satisfaction, and churn risk.
""".strip()


def generate_quantitative_insights(account) -> QuantInsights:
    """Generate structured quantitative insights for an account."""

    user_prompt = f"""
Analyze this customer account's numeric and categorical signals for a QBR.

Account name: {account.account_name}
Plan type: {account.plan_type}
Active users: {account.active_users}
Usage growth QoQ: {account.usage_growth_qoq:.2%}
Automation adoption: {account.automation_adoption_pct:.2%}
Tickets last quarter: {account.tickets_last_quarter}
Average response time (hours): {account.avg_response_time:.1f}
NPS score: {account.nps_score:.1f}
Preferred channel: {account.preferred_channel}
SCAT score: {account.scat_score:.1f}
Risk engine score: {account.risk_engine_score:.2f}

Provide:
- health_status: 2-5 words
- key_metrics: 3-5 bullets as short strings
- growth_trend: one concise sentence
- risk_flags: 1-4 short strings
""".strip()
    return invoke_structured_output(
        system_prompt=QUANT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=QuantInsights,
    )


def run_quant_agent(state: WorkflowState) -> dict[str, dict]:
    """LangGraph node that adds quantitative insights to the workflow state."""

    account = ensure_account(state["account"])
    insights = generate_quantitative_insights(account)
    return {"quantitative_insights": insights.model_dump()}
