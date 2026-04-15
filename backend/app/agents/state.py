"""State definitions and helpers for the QBR workflow."""

from typing import Any, TypedDict

from app.models.customer import CustomerAccount


class WorkflowState(TypedDict, total=False):
    """State carried between LangGraph nodes."""

    account: CustomerAccount | dict[str, Any]
    quantitative_insights: dict[str, Any]
    qualitative_insights: dict[str, Any]
    strategic_synthesis: dict[str, Any]
    judge_verdict: dict[str, Any]
    judge_retry_count: int
    judge_critique: str
    focus_areas: list[str]
    tone: str
    final_draft: str


def ensure_account(account: CustomerAccount | dict[str, Any]) -> CustomerAccount:
    """Normalize raw state input into the canonical customer model."""

    if isinstance(account, CustomerAccount):
        return account
    return CustomerAccount.model_validate(account)
