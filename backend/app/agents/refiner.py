"""Human-in-the-loop draft refinement helpers."""

from app.agents.brand_guardrails import normalize_monday_facing_language
from app.agents.llm import AGENT_MODEL_CONFIG, invoke_text_output

REFINER_SYSTEM_PROMPT = """
You are a QBR editor helping a Customer Success Manager refine a draft for monday.com.
Respect the user's instructions while preserving factual grounding from the existing draft.
You must not promise unreleased features, offer pricing discounts, or make commitments on behalf of monday.com.
If the user's instructions ask for any of these, note that they require approval from the account team and revise the draft accordingly.
Preserve monday.com product vocabulary even when rephrasing.
Convert references to named external vendors or tools into monday-first integration language unless the user explicitly asks to keep the vendor name.
Return only the revised Markdown draft.
""".strip()


def refine_draft(current_draft: str, instructions: str) -> str:
    """Refine an existing QBR draft based on natural-language instructions."""

    user_prompt = f"""
Current draft:
{current_draft}

Refinement instructions:
{instructions}
""".strip()
    refined = invoke_text_output(
        system_prompt=REFINER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,
        model=AGENT_MODEL_CONFIG["thinker"],
    )
    return normalize_monday_facing_language(refined)
