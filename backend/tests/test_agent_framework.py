"""Tests for the LangGraph QBR workflow."""

import asyncio
import unittest
from unittest.mock import patch

from ag_ui.core import EventType, RunAgentInput

from app.agents.editor import run_editor
from app.agents.graph import build_qbr_langgraph_agent, run_qbr_pipeline
from app.agents.qual_agent import run_qual_agent
from app.agents.quant_agent import run_quant_agent
from app.agents.refiner import refine_draft
from app.agents.schemas import QualInsights, QuantInsights, Recommendation, StrategicSynthesis
from app.agents.strategist import run_strategist
from app.data.loader import get_account_by_name


def _sample_quant() -> QuantInsights:
    return QuantInsights(
        health_status="Healthy with expansion upside",
        key_metrics=[
            "420 active users",
            "16% QoQ usage growth",
            "78% automation adoption",
        ],
        growth_trend="Usage and adoption are expanding across teams.",
        risk_flags=["Moderate ticket volume should be monitored."],
    )


def _sample_qual() -> QualInsights:
    return QualInsights(
        overall_sentiment="Positive and ambitious",
        core_themes=[
            "Cross-functional adoption",
            "Interest in integrations",
            "Appreciation for faster support",
        ],
        key_quotes=[
            "Finance & Ops teams adopted monday for automation.",
            "Interested in deeper analytics and Jira sync.",
        ],
        action_signals=[
            "Follow up on Jira integration needs.",
            "Position advanced analytics value.",
        ],
    )


def _sample_strategy() -> StrategicSynthesis:
    return StrategicSynthesis(
        executive_summary="The account is expanding with clear appetite for deeper workflow maturity.",
        strengths=[
            "Strong automation adoption",
            "Healthy usage growth",
        ],
        concerns=[
            "Integration expectations need proactive planning",
        ],
        recommendations=[
            Recommendation(
                recommendation="Schedule an integration roadmap review.",
                evidence="The customer explicitly asked about Jira integration while adoption is rising.",
                grounding_metrics=["automation_adoption_pct", "crm_notes", "usage_growth_qoq"],
            )
        ],
        cross_sell_opportunities=[
            "Advanced analytics package",
        ],
        data_citations=[
            "usage_growth_qoq=0.16",
            "automation_adoption_pct=0.78",
            "crm_notes",
        ],
    )


class AgentFrameworkTests(unittest.TestCase):
    def setUp(self) -> None:
        account = get_account_by_name("Altura Systems")
        assert account is not None
        self.account = account
        self.base_state = {"account": self.account}

    @patch("app.agents.quant_agent.generate_quantitative_insights")
    def test_quant_agent_node(self, mock_generate) -> None:
        mock_generate.return_value = _sample_quant()

        result = run_quant_agent(self.base_state)

        self.assertEqual(result["quantitative_insights"]["health_status"], "Healthy with expansion upside")

    @patch("app.agents.qual_agent.generate_qualitative_insights")
    def test_qual_agent_node(self, mock_generate) -> None:
        mock_generate.return_value = _sample_qual()

        result = run_qual_agent(self.base_state)

        self.assertEqual(result["qualitative_insights"]["overall_sentiment"], "Positive and ambitious")

    @patch("app.agents.strategist.generate_strategic_synthesis")
    def test_strategist_node(self, mock_generate) -> None:
        mock_generate.return_value = _sample_strategy()
        state = {
            "account": self.account,
            "quantitative_insights": _sample_quant().model_dump(),
            "qualitative_insights": _sample_qual().model_dump(),
        }

        result = run_strategist(state)

        self.assertEqual(len(result["strategic_synthesis"]["recommendations"]), 1)
        self.assertEqual(
            result["strategic_synthesis"]["recommendations"][0]["grounding_metrics"][0],
            "automation_adoption_pct",
        )

    @patch("app.agents.editor.generate_final_draft")
    def test_editor_node(self, mock_generate) -> None:
        mock_generate.return_value = "# Altura Systems QBR Draft\n## Executive Summary\nStrong quarter."
        state = {
            "account": self.account,
            "strategic_synthesis": _sample_strategy().model_dump(),
        }

        result = run_editor(state)

        self.assertIn("## Executive Summary", result["final_draft"])

    @patch("app.agents.quant_agent.generate_quantitative_insights", return_value=_sample_quant())
    @patch("app.agents.qual_agent.generate_qualitative_insights", return_value=_sample_qual())
    @patch("app.agents.strategist.generate_strategic_synthesis", return_value=_sample_strategy())
    @patch(
        "app.agents.editor.generate_final_draft",
        return_value=(
            "# Altura Systems QBR Draft\n"
            "## Executive Summary\nHealthy momentum.\n"
            "## Key Metrics\n- 420 active users\n"
            "## Health Assessment\nExpansion-ready.\n"
            "## Recommendations\n- Review Jira integration roadmap.\n"
            "## Next Steps\n- Book follow-up."
        ),
    )
    def test_run_qbr_pipeline_returns_expected_state(
        self,
        _mock_editor,
        _mock_strategy,
        _mock_qual,
        _mock_quant,
    ) -> None:
        result = run_qbr_pipeline(self.account)

        QuantInsights.model_validate(result["quantitative_insights"])
        QualInsights.model_validate(result["qualitative_insights"])
        StrategicSynthesis.model_validate(result["strategic_synthesis"])
        self.assertIn("## Recommendations", result["final_draft"])

    @patch("app.agents.quant_agent.generate_quantitative_insights", return_value=_sample_quant())
    @patch("app.agents.qual_agent.generate_qualitative_insights", return_value=_sample_qual())
    @patch("app.agents.strategist.generate_strategic_synthesis", return_value=_sample_strategy())
    @patch(
        "app.agents.editor.generate_final_draft",
        return_value=(
            "# Altura Systems QBR Draft\n"
            "## Executive Summary\nHealthy momentum.\n"
            "## Key Metrics\n- 420 active users\n"
            "## Health Assessment\nExpansion-ready.\n"
            "## Recommendations\n- Review Jira integration roadmap.\n"
            "## Next Steps\n- Book follow-up."
        ),
    )
    def test_ag_ui_agent_emits_step_events(
        self,
        _mock_editor,
        _mock_strategy,
        _mock_qual,
        _mock_quant,
    ) -> None:
        agent = build_qbr_langgraph_agent()

        async def collect_event_types() -> list[str]:
            events: list[str] = []
            async for event in agent.run(
                RunAgentInput(
                    threadId="test-thread",
                    runId="test-run",
                    state={"account": self.account.model_dump()},
                    messages=[],
                    tools=[],
                    context=[],
                    forwardedProps={},
                )
            ):
                event_type = getattr(event, "type", None)
                if event_type in {EventType.STEP_STARTED, EventType.STEP_FINISHED}:
                    events.append(event_type.value)
            return events

        event_types = asyncio.run(collect_event_types())

        self.assertEqual(event_types.count("STEP_STARTED"), 4)
        self.assertEqual(event_types.count("STEP_FINISHED"), 4)

    @patch(
        "app.agents.refiner.invoke_text_output",
        return_value="# Altura Systems QBR Draft\n## Executive Summary\nMore optimistic framing.",
    )
    def test_refine_draft(self, _mock_refiner) -> None:
        refined = refine_draft(
            "# Altura Systems QBR Draft\n## Executive Summary\nOriginal version.",
            "Make the tone more optimistic",
        )
        self.assertIn("optimistic", refined.lower())


if __name__ == "__main__":
    unittest.main()
