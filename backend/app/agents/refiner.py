"""Human-in-the-loop draft refinement helpers."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_text_output
from app.prompt_templates.refiner import (
    REFINER_SYSTEM_PROMPT,
    render_refiner_user_prompt,
)


def refine_draft(current_draft: str, instructions: str) -> str:
    """Refine an existing QBR draft based on natural-language instructions."""

    user_prompt = render_refiner_user_prompt(
        current_draft=current_draft,
        instructions=instructions,
    )
    refined = invoke_text_output(
        system_prompt=REFINER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,
        model=AGENT_MODEL_CONFIG["thinker"],
    )
    return normalize_monday_facing_language(refined)
