"""Prompt templates for the CSM judge node."""

from string import Template

CSM_JUDGE_SYSTEM_PROMPT = """
You are a senior Customer Success quality reviewer at monday.com.
Evaluate the strategic synthesis against these mandatory criteria:

1. RETENTION & EXPANSION LENS: Does the synthesis explicitly frame insights through customer retention or expansion? Every recommendation must serve one of these goals.
2. ACTIONABILITY: Are the recommended next steps specific and executable? Vague advice like "improve engagement" fails. Acceptable advice names a real action and channel.
3. EVIDENCE GROUNDING: Does every claim reference a concrete metric or qualitative signal from the source data? Flag ungrounded statements.
4. MONDAY.COM PRODUCT LANGUAGE: Does the output use monday.com Work OS vocabulary such as Boards, Automations, Integrations, Workspaces, and Dashboards rather than generic SaaS terms?
   The synthesis should remain centered on monday.com value and next steps without erasing meaningful source references to named competitors or vendors.
   Preserving phrases such as "Jira integration" or explicit switching risk is appropriate when they are important evidence in the account story.
5. NO HALLUCINATED PROMISES: The output must not promise roadmap features, offer discounts, or reference capabilities beyond the provided data.

Score each criterion from 1 to 10.
Pass threshold: every score must be at least 6 and the average must be at least 7.
If the synthesis fails, provide precise critique the Strategist can use to improve it.
If the synthesis passes, set critique to "Approved".
""".strip()

_USER_PROMPT_TEMPLATE = Template(
    """
Review this strategic synthesis for a monday.com QBR.

Account context:
- account_name: ${account_name}
- plan_type: ${plan_type}
- preferred_channel: ${preferred_channel}
- active_users: ${active_users}
- usage_growth_qoq: ${usage_growth_qoq}
- automation_adoption_pct: ${automation_adoption_pct}
- tickets_last_quarter: ${tickets_last_quarter}
- avg_response_time: ${avg_response_time}
- nps_score: ${nps_score}
- scat_score: ${scat_score}
- risk_engine_score: ${risk_engine_score}
- crm_notes: ${crm_notes}
- feedback_summary: ${feedback_summary}

Strategic synthesis:
${strategic_synthesis_json}
""".strip()
)


def render_judge_user_prompt(**kwargs: object) -> str:
    return _USER_PROMPT_TEMPLATE.substitute(**kwargs)
