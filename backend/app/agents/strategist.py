"""Strategic synthesis node for the QBR workflow."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_structured_output
from app.agents.schemas import QualInsights, QuantInsights, StrategicSynthesis
from app.agents.state import WorkflowState, ensure_account

STRATEGIST_SYSTEM_PROMPT = """
You are a senior Customer Success Manager at monday.com preparing strategic QBR recommendations.
Combine quantitative and qualitative findings into a synthesis that reads like a real CSM prepared it.

Rules:
- Every key insight must support either Retention or Expansion. Make that lens explicit.
- Use monday.com Work OS vocabulary throughout: Boards, Automations, Integrations, Workspaces, Dashboards, Work OS.
- Connect metrics to business outcomes. Example: low automation adoption -> manual work remains -> weaker Work OS value -> churn risk.
- Every recommendation must be evidence-grounded and reference specific source metrics or notes.
- Cross-sell or expansion recommendations must reference concrete monday.com capabilities, features, or plan-level value where appropriate.
- Factor the customer's preferred communication channel into engagement recommendations.
- If the source notes mention named external tools or vendors, translate them into monday-first language such as integration workflow needs, cross-functional visibility, or connected development workflows. Do not let external brand names become the headline of the synthesis.
- Do not invent product capabilities, roadmap promises, discounts, or account history beyond the provided inputs.
""".strip()


def generate_strategic_synthesis(
    account,
    quantitative_insights: QuantInsights,
    qualitative_insights: QualInsights,
    *,
    focus_areas: list[str] | None = None,
    judge_critique: str | None = None,
) -> StrategicSynthesis:
    """Generate strategic synthesis for an account."""

    focus_directive = ""
    if focus_areas:
        focus_directive = f"""
--- CSM FOCUS PRIORITIES ---
The CSM has requested emphasis on: {", ".join(focus_areas)}.
Weight your analysis and recommendations toward these areas.
""".strip()

    critique_directive = ""
    if judge_critique:
        critique_directive = f"""
--- REVIEWER FEEDBACK (address all points) ---
{judge_critique}
""".strip()

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

{focus_directive}

{critique_directive}

Provide a concise executive synthesis with:
- strengths: 2-4 items
- concerns: 2-4 items
- recommendations: 2-4 items, each with evidence and grounding_metrics
- cross_sell_opportunities: 1-3 items
- data_citations: references back to source fields or intermediate outputs
""".strip()
    synthesis = invoke_structured_output(
        system_prompt=STRATEGIST_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=StrategicSynthesis,
        temperature=0.3,
        model=AGENT_MODEL_CONFIG["thinker"],
    )
    return synthesis.model_copy(
        update={
            "executive_summary": normalize_monday_facing_language(
                synthesis.executive_summary
            ),
            "strengths": [
                normalize_monday_facing_language(item) for item in synthesis.strengths
            ],
            "concerns": [
                normalize_monday_facing_language(item) for item in synthesis.concerns
            ],
            "recommendations": [
                recommendation.model_copy(
                    update={
                        "recommendation": normalize_monday_facing_language(
                            recommendation.recommendation
                        ),
                        "evidence": normalize_monday_facing_language(
                            recommendation.evidence
                        ),
                        "grounding_metrics": [
                            normalize_monday_facing_language(metric)
                            for metric in recommendation.grounding_metrics
                        ],
                    }
                )
                for recommendation in synthesis.recommendations
            ],
            "cross_sell_opportunities": [
                normalize_monday_facing_language(item)
                for item in synthesis.cross_sell_opportunities
            ],
            "data_citations": [
                normalize_monday_facing_language(item)
                for item in synthesis.data_citations
            ],
        }
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
        focus_areas=state.get("focus_areas", []),
        judge_critique=state.get("judge_critique") or None,
    )
    return {"strategic_synthesis": synthesis.model_dump()}
