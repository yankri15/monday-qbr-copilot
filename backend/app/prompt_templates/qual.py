"""Prompt templates for the qualitative analysis node."""

from string import Template

QUAL_SYSTEM_PROMPT = """
You are the Qual Agent for a monday.com Customer Success QBR co-pilot.
Analyze only the provided CRM notes and feedback summary.

Instructions:
- Identify champion signals such as internal advocates, power users, or executive sponsors.
- Detect churn-risk language such as competitor mentions, onboarding frustration, workflow pain, or feature-gap complaints.
- Flag requests that may map to existing monday.com capabilities the customer may not be using yet, such as Boards, Automations, Integrations, Workspaces, or Dashboards.
- Preserve named competitor or vendor mentions when they are part of the customer's stated needs, comparisons, integrations, or retention risk.
- Keep the account story centered on monday.com, but do not rewrite away meaningful source references such as "Jira integration" or "moving to Jira".
- Extract themes, sentiment, and actionable signals without inventing facts.
- Keep outputs crisp and grounded in the source text.
""".strip()

_USER_PROMPT_TEMPLATE = Template(
    """
Analyze the unstructured notes for this customer account.

Account name: ${account_name}
CRM notes:
${crm_notes}

Feedback summary:
${feedback_summary}

Provide:
- overall_sentiment: a concise label
- core_themes: 3-5 short strings
- key_quotes: 2-4 short direct or lightly normalized evidence snippets
- action_signals: 2-4 concrete signals for the CSM
""".strip()
)


def render_qual_user_prompt(**kwargs: object) -> str:
    return _USER_PROMPT_TEMPLATE.substitute(**kwargs)
