from unittest import TestCase

from scripts.audit_stage5_upload_flow_parity import audit_stage5_upload_flow_parity


class Stage5UploadFlowParityTests(TestCase):
    def test_cli_api_and_frontend_contract_upload_flows_match(self):
        payload = audit_stage5_upload_flow_parity()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["failures"], [])
        self.assertEqual(payload["operation_count"], 6)
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(all(case["cli_matches_backend_core"] for case in payload["operations"]))
        self.assertTrue(all(case["fixture_matches_backend_core"] for case in payload["operations"]))
        if payload["live_fastapi_upload_routes_checked"]:
            self.assertTrue(all(case["live_upload_route_matches_backend_core"] for case in payload["operations"]))
