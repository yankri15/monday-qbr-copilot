"""Human-in-the-loop draft refinement helpers."""

from app.agents.llm import invoke_text_output

REFINER_SYSTEM_PROMPT = """
You are a QBR editor helping a Customer Success Manager refine a draft.
Respect the user's instructions while preserving factual grounding from the existing draft.
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
    return invoke_text_output(
        system_prompt=REFINER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,
    )
