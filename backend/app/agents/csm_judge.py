"""CSM quality-review node for the QBR workflow."""

from app.agents.llm import AGENT_MODEL_CONFIG, invoke_structured_output
from app.agents.schemas import JudgeVerdict, StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account
from app.prompt_templates.judge import (
    CSM_JUDGE_SYSTEM_PROMPT,
    render_judge_user_prompt,
)

MAX_JUDGE_RETRIES = 2


def generate_judge_verdict(
    account,
    strategic_synthesis: StrategicSynthesis,
) -> JudgeVerdict:
    """Review a strategic synthesis against the CSM quality rubric."""

    user_prompt = render_judge_user_prompt(
        account_name=account.account_name,
        plan_type=account.plan_type,
        preferred_channel=account.preferred_channel,
        active_users=account.active_users,
        usage_growth_qoq=f"{account.usage_growth_qoq:.2%}",
        automation_adoption_pct=f"{account.automation_adoption_pct:.2%}",
        tickets_last_quarter=account.tickets_last_quarter,
        avg_response_time=f"{account.avg_response_time:.1f}",
        nps_score=f"{account.nps_score:.1f}",
        scat_score=f"{account.scat_score:.1f}",
        risk_engine_score=f"{account.risk_engine_score:.2f}",
        crm_notes=account.crm_notes,
        feedback_summary=account.feedback_summary,
        strategic_synthesis_json=strategic_synthesis.model_dump_json(indent=2),
    )
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
