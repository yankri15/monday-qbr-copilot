"""Structured outputs for the QBR agent workflow."""

from pydantic import BaseModel, ConfigDict, Field


class QuantInsights(BaseModel):
    """Quantitative account analysis."""

    model_config = ConfigDict(extra="forbid")

    health_status: str = Field(description="Overall health classification")
    key_metrics: list[str] = Field(description="Most important metrics to call out")
    growth_trend: str = Field(description="Short summary of usage and adoption trend")
    risk_flags: list[str] = Field(description="Main risk signals from the metrics")


class QualInsights(BaseModel):
    """Qualitative account analysis."""

    model_config = ConfigDict(extra="forbid")

    overall_sentiment: str = Field(description="Overall sentiment inferred from notes")
    core_themes: list[str] = Field(description="Core recurring themes from notes")
    key_quotes: list[str] = Field(description="Short evidence-grounded snippets or paraphrases")
    action_signals: list[str] = Field(description="Actionable signals for the CSM")


class Recommendation(BaseModel):
    """Action recommendation tied back to evidence."""

    model_config = ConfigDict(extra="forbid")

    recommendation: str = Field(description="Specific recommended next step")
    evidence: str = Field(description="Why this recommendation is justified")
    grounding_metrics: list[str] = Field(
        description="Source metrics or qualitative fields supporting the recommendation"
    )


class StrategicSynthesis(BaseModel):
    """Cross-functional synthesis of the account state."""

    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(description="High-level account narrative")
    strengths: list[str] = Field(description="Positive signs to preserve or expand")
    concerns: list[str] = Field(description="Main concerns or blockers")
    recommendations: list[Recommendation] = Field(
        description="Evidence-grounded next-step recommendations"
    )
    cross_sell_opportunities: list[str] = Field(
        description="Expansion opportunities grounded in the account context"
    )
    data_citations: list[str] = Field(
        description="References back to the source fields and intermediate insights"
    )
