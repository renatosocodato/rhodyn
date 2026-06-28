from unittest import TestCase

from scripts.audit_stage5_frontend_scaffold import audit_stage5_frontend_scaffold


class Stage5FrontendScaffoldTests(TestCase):
    def test_frontend_scaffold_matches_frozen_stage4_contract(self):
        payload = audit_stage5_frontend_scaffold()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["failures"], [])
        self.assertGreaterEqual(payload["openapi_path_count"], 20)
        self.assertEqual(payload["operation_count"], 6)
        self.assertEqual(payload["screen_count"], 8)
        self.assertTrue(all(payload["checks"].values()))
