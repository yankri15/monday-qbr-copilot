"""Prompt templates for the editor node."""

from string import Template

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

_USER_PROMPT_TEMPLATE = Template(
    """
Create a slide-ready QBR draft in Markdown for this customer.

Account context:
- Account name: ${account_name}
- Plan type: ${plan_type}
- Preferred channel: ${preferred_channel}
- Active users: ${active_users}
- Usage growth QoQ: ${usage_growth_qoq}
- Automation adoption: ${automation_adoption_pct}
- Support tickets last quarter: ${tickets_last_quarter}
- Avg response time: ${avg_response_time}
- NPS score: ${nps_score}
- SCAT score: ${scat_score}
- Risk engine score: ${risk_engine_score}
- Audience tone: ${tone}

Strategic synthesis:
${strategic_synthesis_json}

Format with exactly these sections:
# ${account_name} QBR Draft
## Executive Summary
## Key Metrics
## Health Assessment
## Recommendations
## Next Steps

Include concrete evidence and keep each section concise.
""".strip()
)


def render_editor_user_prompt(**kwargs: object) -> str:
    return _USER_PROMPT_TEMPLATE.substitute(**kwargs)
