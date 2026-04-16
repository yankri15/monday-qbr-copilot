"""Qualitative analysis node for the QBR workflow."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_structured_output
from app.agents.schemas import QualInsights
from app.agents.state import WorkflowState, ensure_account
from app.prompt_templates.qual import QUAL_SYSTEM_PROMPT, render_qual_user_prompt


def generate_qualitative_insights(account) -> QualInsights:
    """Generate structured qualitative insights for an account."""

    user_prompt = render_qual_user_prompt(
        account_name=account.account_name,
        crm_notes=account.crm_notes,
        feedback_summary=account.feedback_summary,
    )
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
            "retention_risks": [
                normalize_monday_facing_language(risk)
                for risk in insights.retention_risks
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
