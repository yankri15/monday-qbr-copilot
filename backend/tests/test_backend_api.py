"""Tests for the FastAPI backend layer."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_accounts_endpoint_returns_all_accounts(self) -> None:
        response = self.client.get("/api/accounts")

        self.assertEqual(response.status_code, 200)
        accounts = response.json()
        self.assertEqual(len(accounts), 5)
        self.assertEqual(
            set(accounts[0].keys()),
            {
                "account_name",
                "plan_type",
                "active_users",
                "usage_growth_qoq",
                "automation_adoption_pct",
                "tickets_last_quarter",
                "avg_response_time",
                "nps_score",
                "preferred_channel",
                "scat_score",
                "risk_engine_score",
                "crm_notes",
                "feedback_summary",
            },
        )

    def test_unknown_account_returns_404(self) -> None:
        response = self.client.post(
            "/api/generate-qbr",
            json={"account_name": "Unknown Corp"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Unknown account: Unknown Corp"})

    def test_refine_qbr_endpoint(self) -> None:
        with patch(
            "app.routes.qbr.refine_draft",
            return_value="# Updated Draft\n\nMore optimistic tone.",
        ):
            response = self.client.post(
                "/api/refine-qbr",
                json={
                    "current_draft": "# Draft\n\nOriginal tone.",
                    "instructions": "Make it more optimistic",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"refined_draft": "# Updated Draft\n\nMore optimistic tone."},
        )

    def test_generate_qbr_streams_ag_ui_events(self) -> None:
        from app.agents.schemas import (
            QualInsights,
            QuantInsights,
            Recommendation,
            StrategicSynthesis,
        )

        quant = QuantInsights(
            health_status="Healthy with moderate risk",
            key_metrics=["420 active users", "16% QoQ growth", "78% automation adoption"],
            growth_trend="Usage is growing steadily.",
            risk_flags=["Ticket volume should be watched."],
        )
        qual = QualInsights(
            overall_sentiment="Positive",
            core_themes=["Adoption expansion", "Integration interest"],
            key_quotes=["Asked about Jira integration."],
            action_signals=["Follow up on analytics and Jira sync."],
        )
        strategy = StrategicSynthesis(
            executive_summary="Healthy account with expansion opportunity.",
            strengths=["Cross-team adoption"],
            concerns=["Integration expectations"],
            recommendations=[
                Recommendation(
                    recommendation="Review Jira roadmap",
                    evidence="Customer asked about Jira integration while adoption is strong.",
                    grounding_metrics=["crm_notes", "automation_adoption_pct"],
                )
            ],
            cross_sell_opportunities=["Advanced analytics"],
            data_citations=["crm_notes", "automation_adoption_pct=0.78"],
        )
        draft = (
            "# Altura Systems QBR Draft\n\n"
            "## Executive Summary\nStrong quarter.\n\n"
            "## Key Metrics\n- 420 active users\n\n"
            "## Health Assessment\nHealthy.\n\n"
            "## Recommendations\n- Review Jira roadmap.\n\n"
            "## Next Steps\n- Follow up."
        )

        with patch(
            "app.agents.quant_agent.generate_quantitative_insights",
            return_value=quant,
        ), patch(
            "app.agents.qual_agent.generate_qualitative_insights",
            return_value=qual,
        ), patch(
            "app.agents.strategist.generate_strategic_synthesis",
            return_value=strategy,
        ), patch("app.agents.editor.generate_final_draft", return_value=draft):
            with self.client.stream(
                "POST",
                "/api/generate-qbr",
                json={"account_name": "Altura Systems"},
                headers={"accept": "text/event-stream"},
            ) as response:
                body = "".join(response.iter_text())

        self.assertEqual(response.status_code, 200)
        self.assertIn("event: RUN_STARTED", body)
        self.assertIn("event: STEP_STARTED", body)
        self.assertIn("event: STATE_DELTA", body)
        self.assertIn("event: TEXT_MESSAGE_CONTENT", body)
        self.assertIn("event: RUN_FINISHED", body)
        self.assertIn('"path":"/quantitative_insights"', body)
        self.assertIn('"path":"/qualitative_insights"', body)
        self.assertIn('"path":"/strategic_synthesis"', body)
        self.assertIn("Altura Systems QBR Draft", body)

    def test_cors_allows_localhost_frontend(self) -> None:
        response = self.client.options(
            "/api/accounts",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "http://localhost:3000",
        )


if __name__ == "__main__":
    unittest.main()
