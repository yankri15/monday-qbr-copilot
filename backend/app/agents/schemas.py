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
    retention_risks: list[str] = Field(
        description="Explicit churn, competitor, or workflow-gap risks the CSM should watch"
    )
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


class JudgeScores(BaseModel):
    """Rubric scores for the CSM judge."""

    model_config = ConfigDict(extra="forbid")

    retention_focus: int = Field(description="Score for retention framing from 1 to 10")
    expansion_focus: int = Field(description="Score for expansion framing from 1 to 10")
    actionability: int = Field(description="Score for concrete next steps from 1 to 10")
    evidence_grounding: int = Field(description="Score for evidence grounding from 1 to 10")
    monday_language: int = Field(description="Score for monday.com product language from 1 to 10")


class JudgeVerdict(BaseModel):
    """Structured review output from the CSM quality gate."""

    model_config = ConfigDict(extra="forbid")

    passed: bool = Field(
        description="Whether the synthesis meets the CSM acceptance criteria"
    )
    critique: str = Field(
        description="Specific feedback if failed; 'Approved' if passed"
    )
    scores: JudgeScores = Field(
        description="Rubric scores across the five mandatory quality criteria"
    )
