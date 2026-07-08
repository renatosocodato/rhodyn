import json
import subprocess
import sys
from unittest import TestCase


class ReleaseCheckTests(TestCase):
    def test_release_check_script_passes(self):
        subprocess.run(
            [sys.executable, "scripts/run_stage10_15_author_visual_review_packet.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        result = subprocess.run(
            [sys.executable, "scripts/check_release.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
