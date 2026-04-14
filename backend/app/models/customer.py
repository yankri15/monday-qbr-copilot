"""Typed customer account models loaded from the sample workbook."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlanType = Literal["Enterprise", "Pro", "Basic"]
PreferredChannel = Literal["Email", "Phone", "Chat", "In-app chat"]


class CustomerAccount(BaseModel):
    """Canonical customer record used across the backend."""

    model_config = ConfigDict(extra="forbid")

    account_name: str = Field(description="Customer name")
    plan_type: PlanType = Field(description="Subscription tier")
    active_users: int = Field(ge=0, description="Number of active users")
    usage_growth_qoq: float = Field(
        description="Quarter-over-quarter usage growth as a decimal"
    )
    automation_adoption_pct: float = Field(
        ge=0.0,
        le=1.0,
        description="Automation feature adoption rate",
    )
    tickets_last_quarter: int = Field(
        ge=0, description="Support tickets opened last quarter"
    )
    avg_response_time: float = Field(
        ge=0.0, description="Average support response time in hours"
    )
    nps_score: float = Field(description="Most recent NPS score")
    preferred_channel: PreferredChannel = Field(
        description="Main communication channel preference"
    )
    scat_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Success Confidence & Adoption Trend score",
    )
    risk_engine_score: float = Field(
        ge=0.0,
        le=1.0,
        description="AI-predicted churn risk score",
    )
    crm_notes: str = Field(description="Qualitative notes from the CSM")
    feedback_summary: str = Field(description="Customer feedback summary")
