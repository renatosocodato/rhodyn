import json
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest import TestCase

from rhodyn import ctc_track_cell_id as package_ctc_track_cell_id
from rhodyn.ctc import (
    ctc_features_to_trajectory_records,
    ctc_lineage_coverage_issues,
    ctc_lineage_to_trajectory_records,
    ctc_mask_to_feature_records,
    ctc_sequence_replicate,
    ctc_track_cell_id,
    read_ctc_feature_csv,
    read_ctc_lineage,
    read_uncompressed_grayscale_tiff,
)
from rhodyn.schema import read_trajectory_csv


class CtcAdapterTests(TestCase):
    def _tiny_tiff(self, width, height, bits, pixels):
        pixel_bytes = bytes(pixels) if bits == 8 else struct.pack("<" + "H" * len(pixels), *pixels)
        entries = []

        def add(tag, field_type, count, value):
            entries.append((tag, field_type, count, value))

        entry_count = 9
        pixel_offset = 8 + 2 + entry_count * 12 + 4
        add(256, 4, 1, width)
        add(257, 4, 1, height)
        add(258, 3, 1, bits)
        add(259, 3, 1, 1)
        add(262, 3, 1, 1)
        add(273, 4, 1, pixel_offset)
        add(277, 3, 1, 1)
        add(278, 4, 1, height)
        add(279, 4, 1, len(pixel_bytes))
        header = bytearray(b"II*\x00\x08\x00\x00\x00")
        header.extend(struct.pack("<H", entry_count))
        for row in entries:
            header.extend(struct.pack("<HHII", *row))
        header.extend(struct.pack("<I", 0))
        header.extend(pixel_bytes)
        return bytes(header)

    def test_sequence_aware_ctc_naming_helpers(self):
        self.assertEqual(ctc_track_cell_id("1"), "track_1")
        self.assertEqual(ctc_track_cell_id("1", sequence="00"), "sequence_00_track_1")
        self.assertEqual(package_ctc_track_cell_id("2", sequence="01"), "sequence_01_track_2")
        self.assertEqual(ctc_sequence_replicate("zenodo_7260137"), "zenodo_7260137")
        self.assertEqual(
            ctc_sequence_replicate("zenodo_7260137", sequence="01"),
            "zenodo_7260137_sequence_01",
        )
        self.assertEqual(ctc_sequence_replicate(sequence="03"), "sequence_03")

    def test_mask_to_features_from_uncompressed_tiff_bytes(self):
        mask = read_uncompressed_grayscale_tiff(self._tiny_tiff(3, 2, 16, [0, 1, 1, 2, 2, 2]))
        raw = read_uncompressed_grayscale_tiff(self._tiny_tiff(3, 2, 8, [10, 20, 30, 100, 110, 120]))
        records = ctc_mask_to_feature_records(mask, frame=5, intensity_image=raw, sequence="03")

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].sequence, "03")
        self.assertEqual(records[0].track_id, "1")
        self.assertEqual(records[0].area, 2)
        self.assertAlmostEqual(records[0].x, 1.5)
        self.assertAlmostEqual(records[0].y, 0.0)
        self.assertAlmostEqual(records[0].intensity or 0, 25.0)
        self.assertEqual(records[1].track_id, "2")
        self.assertEqual(records[1].area, 3)
        self.assertAlmostEqual(records[1].x, 1.0)
        self.assertAlmostEqual(records[1].y, 1.0)
        self.assertAlmostEqual(records[1].intensity or 0, 110.0)

    def test_read_ctc_lineage_and_features(self):
        lineage, lineage_issues = read_ctc_lineage("examples/mlci_man_track.txt")
        features, feature_issues = read_ctc_feature_csv("examples/mlci_ctc_features.csv")

        self.assertEqual(lineage_issues, [])
        self.assertEqual(feature_issues, [])
        self.assertEqual(len(lineage), 2)
        self.assertEqual(len(features), 6)
        self.assertEqual(ctc_lineage_coverage_issues(features, lineage), [])

    def test_convert_ctc_features_to_speed_trajectory(self):
        features, issues = read_ctc_feature_csv("examples/mlci_ctc_features.csv")
        self.assertEqual(issues, [])
        records = ctc_features_to_trajectory_records(
            features,
            signal="speed",
            condition="mlci_fixture",
            replicate="schema_fixture",
        )

        self.assertEqual(len(records), 6)
        track_1 = [record.signal for record in records if record.cell_id == "track_1"]
        track_2 = [record.signal for record in records if record.cell_id == "track_2"]
        self.assertEqual(track_1, [0.0, 5.0, 5.0])
        self.assertEqual(track_2, [0.0, 3.0, 4.0])
        self.assertTrue(all(record.condition == "mlci_fixture" for record in records))

    def test_convert_ctc_features_preserves_sequence_grouping(self):
        features = [
            *ctc_mask_to_feature_records(
                read_uncompressed_grayscale_tiff(self._tiny_tiff(2, 1, 16, [1, 0])),
                frame=0,
                sequence="00",
            ),
            *ctc_mask_to_feature_records(
                read_uncompressed_grayscale_tiff(self._tiny_tiff(2, 1, 16, [1, 0])),
                frame=0,
                sequence="01",
            ),
        ]
        records = ctc_features_to_trajectory_records(
            features,
            signal="area",
            condition="mlci_fixture",
            replicate="zenodo_7260137",
        )

        self.assertEqual([record.cell_id for record in records], ["sequence_00_track_1", "sequence_01_track_1"])
        self.assertEqual(
            [record.replicate for record in records],
            ["zenodo_7260137_sequence_00", "zenodo_7260137_sequence_01"],
        )

    def test_cli_ctc_to_trajectory_writes_valid_trajectory_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "trajectory.csv"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rhodyn.cli",
                    "ctc-to-trajectory",
                    "examples/mlci_ctc_features.csv",
                    "--lineage",
                    "examples/mlci_man_track.txt",
                    "--signal",
                    "speed",
                    "--condition",
                    "mlci_fixture",
                    "--replicate",
                    "schema_fixture",
                    "--output",
                    str(output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(result.stdout)
            rows, issues = read_trajectory_csv(output)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["trajectory_rows"], 6)
        self.assertEqual(issues, [])
        self.assertEqual(len(rows), 6)

    def test_public_lineage_subset_converts_to_normalized_age_trajectory(self):
        lineage, issues = read_ctc_lineage("case_studies/mlci_public_man_track_subset.txt")
        self.assertEqual(issues, [])
        records = ctc_lineage_to_trajectory_records(
            lineage,
            signal="normalized_track_age",
            condition="mlci_public_lineage_subset",
            replicate="zenodo_7260137",
            max_tracks=10,
        )

        self.assertGreater(len(records), 10)
        self.assertTrue(all(0 <= record.signal <= 1 for record in records))
        self.assertTrue(all(record.condition == "mlci_public_lineage_subset" for record in records))

    def test_cli_ctc_lineage_to_trajectory_writes_valid_trajectory_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "public_lineage_trajectory.csv"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rhodyn.cli",
                    "ctc-lineage-to-trajectory",
                    "case_studies/mlci_public_man_track_subset.txt",
                    "--signal",
                    "normalized_track_age",
                    "--condition",
                    "mlci_public_lineage_subset",
                    "--replicate",
                    "zenodo_7260137",
                    "--max-tracks",
                    "10",
                    "--output",
                    str(output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(result.stdout)
            rows, issues = read_trajectory_csv(output)

        self.assertEqual(payload["status"], "pass")
        self.assertGreater(payload["trajectory_rows"], 10)
        self.assertEqual(issues, [])
        self.assertEqual(len(rows), payload["trajectory_rows"])

    def test_public_segmentation_feature_subset_converts_to_intensity_and_speed(self):
        features, feature_issues = read_ctc_feature_csv("case_studies/mlci_public_track_features_subset.csv")
        self.assertEqual(feature_issues, [])
        self.assertEqual(len(features), 62)
        self.assertEqual(sorted({feature.sequence for feature in features}), ["00", "01"])
        self.assertTrue(all(feature.intensity is not None for feature in features))

        intensity_records = ctc_features_to_trajectory_records(
            features,
            signal="intensity",
            condition="mlci_public_segmentation_features",
            replicate="zenodo_7260137",
        )
        speed_records = ctc_features_to_trajectory_records(
            features,
            signal="speed",
            condition="mlci_public_segmentation_features",
            replicate="zenodo_7260137",
        )

        self.assertEqual(len(intensity_records), len(features))
        self.assertEqual(len(speed_records), len(features))
        self.assertTrue(all(record.signal >= 0 for record in speed_records))
        self.assertEqual(
            sorted({record.replicate for record in intensity_records}),
            ["zenodo_7260137_sequence_00", "zenodo_7260137_sequence_01"],
        )
        self.assertTrue(all(record.cell_id.startswith("sequence_") for record in intensity_records))

    def test_public_case_study_ships_no_raw_image_or_archive_payloads(self):
        allowed_analysis_bundles = {
            Path("case_studies/stage7_usability_rehearsal/biologist_residence_bundle.zip"),
            Path("case_studies/stage7_usability_rehearsal/quantitative_bounded_coupling_bundle.zip"),
        }
        expected_bundle_members = {
            "README.md",
            "input_rows.csv",
            "manifest.json",
            "parameter_provenance.json",
            "parameter_provenance.md",
            "parameters.json",
            "report.md",
            "result.json",
            "result_rows.csv",
        }
        forbidden_suffixes = {".tif", ".tiff", ".zip"}
        shipped_payloads = [
            path
            for path in Path("case_studies").rglob("*")
            if path.is_file()
            and path.suffix.lower() in forbidden_suffixes
            and path not in allowed_analysis_bundles
        ]
        self.assertEqual(shipped_payloads, [])
        for bundle in allowed_analysis_bundles:
            self.assertTrue(bundle.exists(), bundle)
            with zipfile.ZipFile(bundle) as archive:
                self.assertEqual(set(archive.namelist()), expected_bundle_members)
                self.assertFalse(any(name.lower().endswith((".tif", ".tiff", ".lif", ".czi", ".nd2", ".prism", ".xml", ".zip")) for name in archive.namelist()))

    def test_public_case_study_workflow_runs(self):
        result = subprocess.run(
            [sys.executable, "examples/mlci_public_case_study_workflow.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["trajectory_rows"], 6)
        self.assertIn("public_subset", payload)
        self.assertEqual(payload["public_subset"]["feature_rows"], 62)
        self.assertEqual(payload["public_subset"]["sequences"], ["00", "01"])
        self.assertEqual(
            payload["public_subset"]["trajectory_replicates"],
            ["zenodo_7260137_sequence_00", "zenodo_7260137_sequence_01"],
        )
        self.assertEqual(payload["public_subset"]["intensity_trajectory_rows"], 62)
        self.assertEqual(payload["public_subset"]["speed_trajectory_rows"], 62)
        self.assertIn("public_lineage_fallback", payload)
        self.assertGreater(payload["public_lineage_fallback"]["trajectory_rows"], 10)
        self.assertIn("segmentation-derived features demonstrate", payload["interpretation_boundary"])
        self.assertIn(payload["plot_status"], {"matplotlib_not_installed", "plot_constructed_without_display"})
