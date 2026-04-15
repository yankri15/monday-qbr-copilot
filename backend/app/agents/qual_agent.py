"""Qualitative analysis node for the QBR workflow."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_structured_output
from app.agents.schemas import QualInsights
from app.agents.state import WorkflowState, ensure_account

QUAL_SYSTEM_PROMPT = """
You are the Qual Agent for a monday.com Customer Success QBR co-pilot.
Analyze only the provided CRM notes and feedback summary.

Instructions:
- Identify champion signals such as internal advocates, power users, or executive sponsors.
- Detect churn-risk language such as competitor mentions, onboarding frustration, workflow pain, or feature-gap complaints.
- Flag requests that may map to existing monday.com capabilities the customer may not be using yet, such as Boards, Automations, Integrations, Workspaces, or Dashboards.
- If source notes mention a named external tool or vendor, convert that into monday-first language such as "integration workflow", "cross-system visibility", or "development workflow connection". Do not surface third-party brand names in your output.
- Extract themes, sentiment, and actionable signals without inventing facts.
- Keep outputs crisp and grounded in the source text.
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
    insights = invoke_structured_output(
        system_prompt=QUAL_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=QualInsights,
        model=AGENT_MODEL_CONFIG["extractor"],
    )
    return insights.model_copy(
        update={
            "overall_sentiment": normalize_monday_facing_language(insights.overall_sentiment),
            "core_themes": [
                normalize_monday_facing_language(theme) for theme in insights.core_themes
            ],
            "key_quotes": [
                normalize_monday_facing_language(quote) for quote in insights.key_quotes
            ],
            "action_signals": [
                normalize_monday_facing_language(signal)
                for signal in insights.action_signals
            ],
        }
    )


def run_qual_agent(state: WorkflowState) -> dict[str, dict]:
    """LangGraph node that adds qualitative insights to the workflow state."""

    account = ensure_account(state["account"])
    insights = generate_qualitative_insights(account)
    return {"qualitative_insights": insights.model_dump()}
