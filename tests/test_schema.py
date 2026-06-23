import tempfile
from pathlib import Path
from unittest import TestCase

from rhodyn.schema import (
    COUPLING_SCHEMA,
    RESERVE_SCHEMA,
    TRAJECTORY_SCHEMA,
    read_coupling_csv,
    read_reserve_csv,
    read_trajectory_csv,
    schema_specs,
)


def _csv(text: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return Path(handle.name)


class SchemaTests(TestCase):
    def test_schema_specs_expose_stable_input_roles(self):
        specs = schema_specs()
        self.assertEqual(specs["trajectory"], TRAJECTORY_SCHEMA)
        self.assertEqual(specs["reserve"], RESERVE_SCHEMA)
        self.assertEqual(specs["coupling"], COUPLING_SCHEMA)
        self.assertIn("cell_id", specs["trajectory"].required)
        self.assertIn("replicate", specs["reserve"].optional)

    def test_trajectory_validation_reports_grouping_and_time_issues(self):
        path = _csv("cell_id,time,condition,signal\n,0,control,0.2\ncell_2,-1,,inf\n")
        try:
            rows, issues = read_trajectory_csv(path)
        finally:
            path.unlink()
        self.assertEqual(len(rows), 2)
        messages = {(issue.field, issue.message) for issue in issues}
        self.assertIn(("cell_id", "empty cell identifier"), messages)
        self.assertIn(("condition", "empty condition identifier"), messages)
        self.assertIn(("time", "time must be non-negative"), messages)
        self.assertIn(("signal", "expected finite numeric value, got 'inf'"), messages)

    def test_missing_required_column_reports_each_field(self):
        path = _csv("cell_id,time,condition\ncell_1,0,control\n")
        try:
            rows, issues = read_trajectory_csv(path)
        finally:
            path.unlink()
        self.assertEqual(rows, [])
        self.assertEqual([(issue.field, issue.message) for issue in issues], [("signal", "missing required trajectory column")])

    def test_reserve_schema_validates_response_table(self):
        path = _csv("sample_id,time,condition,response,replicate\ns1,0,stim,1.2,r1\ns2,1,stim,1.5,r1\n")
        try:
            rows, issues = read_reserve_csv(path)
        finally:
            path.unlink()
        self.assertEqual(issues, [])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].replicate, "r1")

    def test_coupling_schema_validates_margin_and_optional_rope(self):
        path = _csv("contrast,estimate,ci_low,ci_high,margin,rope_mass\nrock_src,0.01,-0.02,0.03,0,0.99\n")
        try:
            rows, issues = read_coupling_csv(path)
        finally:
            path.unlink()
        self.assertEqual(len(rows), 1)
        self.assertIn(("margin", "margin must be positive"), {(issue.field, issue.message) for issue in issues})
        self.assertEqual(rows[0].rope_mass, 0.99)
