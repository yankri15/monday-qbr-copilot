"""CSM quality-review node for the QBR workflow."""

from app.agents.llm import AGENT_MODEL_CONFIG, invoke_structured_output
from app.agents.schemas import JudgeVerdict, StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account

MAX_JUDGE_RETRIES = 2

CSM_JUDGE_SYSTEM_PROMPT = """
You are a senior Customer Success quality reviewer at monday.com.
Evaluate the strategic synthesis against these mandatory criteria:

1. RETENTION & EXPANSION LENS: Does the synthesis explicitly frame insights through customer retention or expansion? Every recommendation must serve one of these goals.
2. ACTIONABILITY: Are the recommended next steps specific and executable? Vague advice like "improve engagement" fails. Acceptable advice names a real action and channel.
3. EVIDENCE GROUNDING: Does every claim reference a concrete metric or qualitative signal from the source data? Flag ungrounded statements.
4. MONDAY.COM PRODUCT LANGUAGE: Does the output use monday.com Work OS vocabulary such as Boards, Automations, Integrations, Workspaces, and Dashboards rather than generic SaaS terms?
   If source notes mention a named external tool or vendor, the synthesis should translate that into monday-first integration language rather than making the third-party brand the center of the story.
5. NO HALLUCINATED PROMISES: The output must not promise roadmap features, offer discounts, or reference capabilities beyond the provided data.

Score each criterion from 1 to 10.
Pass threshold: every score must be at least 6 and the average must be at least 7.
If the synthesis fails, provide precise critique the Strategist can use to improve it.
If the synthesis passes, set critique to "Approved".
""".strip()


def generate_judge_verdict(
    account,
    strategic_synthesis: StrategicSynthesis,
) -> JudgeVerdict:
    """Review a strategic synthesis against the CSM quality rubric."""

    user_prompt = f"""
Review this strategic synthesis for a monday.com QBR.

Account context:
- account_name: {account.account_name}
- plan_type: {account.plan_type}
- preferred_channel: {account.preferred_channel}
- active_users: {account.active_users}
- usage_growth_qoq: {account.usage_growth_qoq:.2%}
- automation_adoption_pct: {account.automation_adoption_pct:.2%}
- tickets_last_quarter: {account.tickets_last_quarter}
- avg_response_time: {account.avg_response_time:.1f}
- nps_score: {account.nps_score:.1f}
- scat_score: {account.scat_score:.1f}
- risk_engine_score: {account.risk_engine_score:.2f}
- crm_notes: {account.crm_notes}
- feedback_summary: {account.feedback_summary}

Strategic synthesis:
{strategic_synthesis.model_dump_json(indent=2)}
""".strip()
    return invoke_structured_output(
        system_prompt=CSM_JUDGE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=JudgeVerdict,
        model=AGENT_MODEL_CONFIG["thinker"],
    )


def run_csm_judge(state: WorkflowState) -> dict[str, object]:
    """LangGraph node that evaluates the strategic synthesis quality."""

    account = ensure_account(state["account"])
    strategic_synthesis = StrategicSynthesis.model_validate(state["strategic_synthesis"])
    verdict = generate_judge_verdict(account, strategic_synthesis)
    retry_count = int(state.get("judge_retry_count", 0)) + 1

    return {
        "judge_verdict": verdict.model_dump(),
        "judge_retry_count": retry_count,
        "judge_critique": verdict.critique,
    }


def judge_router(state: WorkflowState) -> str:
    """Choose whether to retry the strategist or continue to the editor."""

    verdict = JudgeVerdict.model_validate(state["judge_verdict"])
    if verdict.passed:
        return "editor"
    if state.get("judge_retry_count", 0) >= MAX_JUDGE_RETRIES:
        return "editor"
    return "strategist"
