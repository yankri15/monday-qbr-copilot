"""Qualitative analysis node for the QBR workflow."""

from app.agents.llm import invoke_structured_output
from app.agents.schemas import QualInsights
from app.agents.state import WorkflowState, ensure_account

QUAL_SYSTEM_PROMPT = """
You are the Qual Agent for a customer-success QBR copilot.
Analyze only the provided CRM notes and feedback summary.
Extract themes, sentiment, and actionable signals without inventing facts.
Keep outputs crisp and grounded in the source text.
""".strip()


def generate_qualitative_insights(account) -> QualInsights:
    """Generate structured qualitative insights for an account."""

    user_prompt = f"""
Analyze the unstructured notes for this customer account.

Account name: {account.account_name}
CRM notes:
{account.crm_notes}

Feedback summary:
{account.feedback_summary}

Provide:
- overall_sentiment: a concise label
- core_themes: 3-5 short strings
- key_quotes: 2-4 short direct or lightly normalized evidence snippets
- action_signals: 2-4 concrete signals for the CSM
""".strip()
    return invoke_structured_output(
        system_prompt=QUAL_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=QualInsights,
    )


def run_qual_agent(state: WorkflowState) -> dict[str, dict]:
    """LangGraph node that adds qualitative insights to the workflow state."""

    account = ensure_account(state["account"])
    insights = generate_qualitative_insights(account)
    return {"qualitative_insights": insights.model_dump()}
