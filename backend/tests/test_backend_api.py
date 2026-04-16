"""Tests for the FastAPI backend layer."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.data.upload_store import clear_uploads
from app.main import app

VALID_CSV = """account_name,plan_type,active_users,usage_growth_qoq,automation_adoption_pct,tickets_last_quarter,avg_response_time,nps_score,preferred_channel,scat_score,risk_engine_score,crm_notes,feedback_summary
Northwind Ops,Enterprise,128,0.12,0.41,4,3.2,8.1,Email,79,0.28,Team expanding into more workflows,Positive feedback on dashboards
"""

UPDATED_VALID_CSV = """account_name,plan_type,active_users,usage_growth_qoq,automation_adoption_pct,tickets_last_quarter,avg_response_time,nps_score,preferred_channel,scat_score,risk_engine_score,crm_notes,feedback_summary
Northwind Ops,Enterprise,144,0.18,0.52,3,2.4,8.8,Email,86,0.19,Updated account file with stronger adoption,Positive feedback after automation rollout
"""


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_uploads()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        clear_uploads()

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
                "account_source",
                "upload_id",
            },
        )

    def test_unknown_account_returns_404(self) -> None:
        response = self.client.post(
            "/api/generate-qbr",
            json={"account_name": "Unknown Corp"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Unknown account: Unknown Corp"})

    def test_upload_data_accepts_valid_csv(self) -> None:
        response = self.client.post(
            "/api/upload-data",
            files={"file": ("northwind.csv", VALID_CSV, "text/csv")},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload["upload_id"])
        self.assertEqual(len(payload["accounts"]), 1)
        self.assertEqual(payload["accounts"][0]["account_name"], "Northwind Ops")
        self.assertEqual(payload["accounts"][0]["account_source"], "uploaded")

    def test_upload_data_rejects_mismatched_headers(self) -> None:
        invalid_csv = "name,plan_type\nNorthwind Ops,Enterprise\n"

        response = self.client.post(
            "/api/upload-data",
            files={"file": ("broken.csv", invalid_csv, "text/csv")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Unexpected workbook schema", response.json()["detail"])

    def test_accounts_endpoint_merges_uploaded_accounts(self) -> None:
        upload_response = self.client.post(
            "/api/upload-data",
            files={"file": ("northwind.csv", VALID_CSV, "text/csv")},
        )
        self.assertEqual(upload_response.status_code, 201)

        response = self.client.get("/api/accounts")

        self.assertEqual(response.status_code, 200)
        accounts = response.json()
        self.assertEqual(len(accounts), 6)
        northwind = next(
            account for account in accounts if account["account_name"] == "Northwind Ops"
        )
        self.assertEqual(northwind["account_source"], "uploaded")
        self.assertIsNotNone(northwind["upload_id"])

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
            JudgeVerdict,
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
            key_quotes=["Asked about stronger development workflow connectivity."],
            retention_risks=["Interest in Jira suggests a workflow-ownership gap."],
            action_signals=["Follow up on analytics and integration workflow needs."],
        )
        strategy = StrategicSynthesis(
            executive_summary="Healthy account with expansion opportunity.",
            strengths=["Cross-team adoption"],
            concerns=["Integration expectations"],
            recommendations=[
                Recommendation(
                    recommendation="Review integration roadmap",
                    evidence="Customer asked for stronger development workflow connectivity while adoption is strong.",
                    grounding_metrics=["crm_notes", "automation_adoption_pct"],
                )
            ],
            cross_sell_opportunities=["Advanced analytics"],
            data_citations=["crm_notes", "automation_adoption_pct=0.78"],
        )
        verdict = JudgeVerdict(
            passed=True,
            critique="Approved",
            scores={
                "retention_focus": 8,
                "expansion_focus": 8,
                "actionability": 8,
                "evidence_grounding": 9,
                "monday_language": 8,
            },
        )
        draft = (
            "# Altura Systems QBR Draft\n\n"
            "## Executive Summary\nStrong quarter.\n\n"
            "## Key Metrics\n- 420 active users\n\n"
            "## Health Assessment\nHealthy.\n\n"
            "## Recommendations\n- Review integration roadmap.\n\n"
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
        ), patch(
            "app.agents.csm_judge.generate_judge_verdict",
            return_value=verdict,
        ), patch("app.agents.editor.generate_final_draft", return_value=draft):
            with self.client.stream(
                "POST",
                "/api/generate-qbr",
                json={
                    "account_name": "Altura Systems",
                    "focus_areas": ["upsell_opportunity"],
                    "tone": "executive",
                },
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
        self.assertIn('"path":"/judge_verdict"', body)
        self.assertIn("Altura Systems QBR Draft", body)

    def test_generate_qbr_uses_uploaded_account_when_available(self) -> None:
        upload_response = self.client.post(
            "/api/upload-data",
            files={"file": ("northwind.csv", VALID_CSV, "text/csv")},
        )
        self.assertEqual(upload_response.status_code, 201)

        with patch(
            "app.routes.qbr.build_qbr_langgraph_agent",
            side_effect=RuntimeError("agent should not be built in this test"),
        ), patch(
            "app.routes.qbr._generate_qbr_stream",
            return_value=iter(()),
        ) as stream_mock:
            response = self.client.post(
                "/api/generate-qbr",
                json={"account_name": "Northwind Ops"},
            )

        self.assertEqual(response.status_code, 200)
        streamed_account = stream_mock.call_args.kwargs["account"]
        self.assertEqual(streamed_account.account_name, "Northwind Ops")

    def test_generate_qbr_accepts_frontend_account_payload_shape(self) -> None:
        with patch(
            "app.routes.qbr._generate_qbr_stream",
            return_value=iter(()),
        ) as stream_mock:
            response = self.client.post(
                "/api/generate-qbr",
                json={
                    "account_name": "Altura Systems",
                    "account": {
                        "account_name": "Altura Systems",
                        "plan_type": "Enterprise",
                        "active_users": 420,
                        "usage_growth_qoq": 0.16,
                        "automation_adoption_pct": 0.78,
                        "tickets_last_quarter": 38,
                        "avg_response_time": 3.2,
                        "nps_score": 8.3,
                        "preferred_channel": "Email",
                        "scat_score": 84.0,
                        "risk_engine_score": 0.18,
                        "crm_notes": "Strong quarter.",
                        "feedback_summary": "Interested in deeper analytics.",
                        "account_source": "sample",
                        "upload_id": None,
                    },
                },
            )

        self.assertEqual(response.status_code, 200)
        streamed_account = stream_mock.call_args.kwargs["account"]
        self.assertEqual(streamed_account.account_name, "Altura Systems")
        self.assertEqual(streamed_account.plan_type, "Enterprise")

    def test_generate_qbr_prefers_latest_uploaded_version_for_duplicate_name(self) -> None:
        first_upload = self.client.post(
            "/api/upload-data",
            files={"file": ("northwind.csv", VALID_CSV, "text/csv")},
        )
        second_upload = self.client.post(
            "/api/upload-data",
            files={"file": ("northwind-refresh.csv", UPDATED_VALID_CSV, "text/csv")},
        )

        self.assertEqual(first_upload.status_code, 201)
        self.assertEqual(second_upload.status_code, 201)

        with patch(
            "app.routes.qbr._generate_qbr_stream",
            return_value=iter(()),
        ) as stream_mock:
            response = self.client.post(
                "/api/generate-qbr",
                json={"account_name": "Northwind Ops"},
            )

        self.assertEqual(response.status_code, 200)
        streamed_account = stream_mock.call_args.kwargs["account"]
        self.assertEqual(streamed_account.active_users, 144)
        self.assertAlmostEqual(streamed_account.risk_engine_score, 0.19)

    def test_generate_qbr_uses_primary_stream_for_vercel_host(self) -> None:
        async def empty_stream():
            if False:
                yield ""

        with patch(
            "app.routes.qbr._generate_qbr_stream",
            return_value=empty_stream(),
        ) as stream_mock:
            response = self.client.post(
                "/api/generate-qbr",
                json={"account_name": "Altura Systems"},
                headers={"host": "monday-qbr-copilot.vercel.app"},
            )

        self.assertEqual(response.status_code, 200)
        stream_mock.assert_called_once()

    def test_export_pdf_endpoint_returns_pdf_attachment(self) -> None:
        with patch(
            "app.routes.export.markdown_to_pdf",
            return_value=b"%PDF-1.7 fake pdf",
        ):
            response = self.client.post(
                "/api/export-pdf",
                json={
                    "markdown_content": "# QBR Draft\n\nExecutive summary.",
                    "account_name": "Altura Systems",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn("Altura Systems_QBR.pdf", response.headers["content-disposition"])
        self.assertEqual(response.content, b"%PDF-1.7 fake pdf")

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
