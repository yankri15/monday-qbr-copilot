"""Strategic synthesis node for the QBR workflow."""

from app.agents.llm import invoke_structured_output
from app.agents.schemas import QualInsights, QuantInsights, StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account

STRATEGIST_SYSTEM_PROMPT = """
You are the Strategist Agent for a customer-success QBR copilot.
Combine quantitative and qualitative findings into an executive-level synthesis.
Every recommendation must be evidence-grounded and reference specific source metrics or notes.
Factor the customer's preferred communication channel into engagement recommendations.
Do not invent product capabilities or account history beyond the provided inputs.
""".strip()


def generate_strategic_synthesis(
    account,
    quantitative_insights: QuantInsights,
    qualitative_insights: QualInsights,
) -> StrategicSynthesis:
    """Generate strategic synthesis for an account."""

    user_prompt = f"""
Synthesize the following account data into a strategic QBR view.

Account name: {account.account_name}
Plan type: {account.plan_type}
Preferred channel: {account.preferred_channel}

Quantitative insights:
{quantitative_insights.model_dump_json(indent=2)}

Qualitative insights:
{qualitative_insights.model_dump_json(indent=2)}

Original source metrics:
- active_users: {account.active_users}
- usage_growth_qoq: {account.usage_growth_qoq:.2%}
- automation_adoption_pct: {account.automation_adoption_pct:.2%}
- tickets_last_quarter: {account.tickets_last_quarter}
- avg_response_time: {account.avg_response_time:.1f}
- nps_score: {account.nps_score:.1f}
- scat_score: {account.scat_score:.1f}
- risk_engine_score: {account.risk_engine_score:.2f}

Provide a concise executive synthesis with:
- strengths: 2-4 items
- concerns: 2-4 items
- recommendations: 2-4 items, each with evidence and grounding_metrics
- cross_sell_opportunities: 1-3 items
- data_citations: references back to source fields or intermediate outputs
""".strip()
    return invoke_structured_output(
        system_prompt=STRATEGIST_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=StrategicSynthesis,
    )


def run_strategist(state: WorkflowState) -> dict[str, dict]:
    """LangGraph node that combines quant + qual into a strategic synthesis."""

    account = ensure_account(state["account"])
    quantitative_insights = QuantInsights.model_validate(state["quantitative_insights"])
    qualitative_insights = QualInsights.model_validate(state["qualitative_insights"])
    synthesis = generate_strategic_synthesis(
        account,
        quantitative_insights,
        qualitative_insights,
    )
    return {"strategic_synthesis": synthesis.model_dump()}
