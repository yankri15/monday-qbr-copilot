"""Editorial node for formatting the final QBR markdown draft."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_text_output
from app.agents.schemas import StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account
from app.prompt_templates.editor import EDITOR_SYSTEM_PROMPT, render_editor_user_prompt


def generate_final_draft(
    account,
    strategic_synthesis: StrategicSynthesis,
    *,
    tone: str = "executive",
) -> str:
    """Generate the final markdown QBR draft."""

    user_prompt = render_editor_user_prompt(
        account_name=account.account_name,
        plan_type=account.plan_type,
        preferred_channel=account.preferred_channel,
        active_users=account.active_users,
        usage_growth_qoq=f"{account.usage_growth_qoq:.2%}",
        automation_adoption_pct=f"{account.automation_adoption_pct:.2%}",
        tickets_last_quarter=account.tickets_last_quarter,
        avg_response_time=f"{account.avg_response_time:.1f} hours",
        nps_score=f"{account.nps_score:.1f}",
        scat_score=f"{account.scat_score:.1f}",
        risk_engine_score=f"{account.risk_engine_score:.2f}",
        tone=tone,
        strategic_synthesis_json=strategic_synthesis.model_dump_json(indent=2),
    )
    draft = invoke_text_output(
        system_prompt=EDITOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        model=AGENT_MODEL_CONFIG["thinker"],
    )
    return normalize_monday_facing_language(draft)


def run_editor(state: WorkflowState) -> dict[str, str]:
    """LangGraph node that formats the final markdown draft."""

    account = ensure_account(state["account"])
    strategic_synthesis = StrategicSynthesis.model_validate(state["strategic_synthesis"])
    draft = generate_final_draft(
        account,
        strategic_synthesis,
        tone=state.get("tone", "executive"),
    )
    return {"final_draft": draft}
