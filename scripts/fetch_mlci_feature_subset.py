"""Derive a small MLCI feature subset without storing raw TIFF downloads."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

from fetch_mlci_lineage_subset import ZENODO_CTC_ZIP_URL, _central_directory, _content_length, _fetch_range, _find_entry

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.ctc import ctc_mask_to_feature_records, read_ctc_lineage, read_uncompressed_grayscale_tiff


DEFAULT_FRAMES = "0:140:10"


class ZipRangeReader:
    """Read selected ZIP entries with one central-directory lookup."""

    def __init__(self, url: str):
        self.url = url
        size = _content_length(url)
        self.central_directory = _central_directory(url, size)

    def extract(self, entry_name: str) -> bytes:
        method, compressed_size, local_offset = _find_entry(self.central_directory, entry_name)
        local_header = _fetch_range(self.url, local_offset, local_offset + 4096)
        if local_header[:4] != b"PK\x03\x04":
            raise ValueError("bad local-file header")
        values = struct.unpack("<4sHHHHHIIIHH", local_header[:30])
        name_len = values[9]
        extra_len = values[10]
        data_start = local_offset + 30 + name_len + extra_len
        compressed = _fetch_range(self.url, data_start, data_start + compressed_size - 1)
        if method == 0:
            return compressed
        if method == 8:
            return zlib.decompress(compressed, -15)
        raise ValueError(f"unsupported ZIP compression method: {method}")


def _parse_frames(value: str) -> list[int]:
    frames: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            pieces = [int(piece) for piece in part.split(":")]
            if len(pieces) not in {2, 3}:
                raise ValueError("frame ranges must use start:end or start:end:step")
            start, end = pieces[0], pieces[1]
            step = pieces[2] if len(pieces) == 3 else 1
            if step <= 0:
                raise ValueError("frame range step must be positive")
            frames.extend(range(start, end + 1, step))
        else:
            frames.append(int(part))
    if any(frame < 0 for frame in frames):
        raise ValueError("frames must be non-negative")
    if not frames:
        raise ValueError("at least one frame is required")
    return sorted(set(frames))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=ZENODO_CTC_ZIP_URL)
    parser.add_argument("--sequence", default="00")
    parser.add_argument("--frames", default=DEFAULT_FRAMES, help="Comma-separated frames or inclusive ranges like 0:140:10.")
    parser.add_argument("--label-source", choices=["TRA", "SEG"], default="TRA")
    parser.add_argument("--lineage-filter", default="", help="Optional CTC lineage table used to keep known track ids.")
    parser.add_argument("--include-intensity", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provenance", default="")
    args = parser.parse_args()

    frames = _parse_frames(args.frames)
    allowed_track_ids: set[str] | None = None
    lineage_rows = 0
    if args.lineage_filter:
        lineage, issues = read_ctc_lineage(args.lineage_filter)
        if issues:
            raise ValueError(f"lineage filter has validation issues: {issues}")
        allowed_track_ids = {row.track_id for row in lineage}
        lineage_rows = len(lineage)

    output = Path(args.output)
    records = []
    extracted_entries: list[str] = []
    reader = ZipRangeReader(args.url)
    for frame in frames:
        if args.label_source == "TRA":
            mask_entry = f"{args.sequence}_GT/TRA/man_track{frame:04d}.tif"
        else:
            mask_entry = f"{args.sequence}_GT/SEG/man_seg{frame:04d}.tif"
        raw_entry = f"{args.sequence}/t{frame:04d}.tif"

        mask = read_uncompressed_grayscale_tiff(reader.extract(mask_entry))
        intensity = None
        extracted_entries.append(mask_entry)
        if args.include_intensity:
            intensity = read_uncompressed_grayscale_tiff(reader.extract(raw_entry))
            extracted_entries.append(raw_entry)
        records.extend(
            ctc_mask_to_feature_records(
                mask,
                frame=frame,
                intensity_image=intensity,
                allowed_track_ids=allowed_track_ids,
            )
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["track_id", "frame", "x", "y", "area", "intensity"], lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "track_id": record.track_id,
                    "frame": record.frame,
                    "x": f"{record.x:.6f}",
                    "y": f"{record.y:.6f}",
                    "area": f"{record.area:.0f}",
                    "intensity": "" if record.intensity is None else f"{record.intensity:.6f}",
                }
            )

    provenance = {
        "source": "Tracking one-in-a-million microbial single-cell tracking benchmark",
        "zenodo_record": "https://zenodo.org/records/7260137",
        "zip_url": args.url,
        "license": "CC-BY-4.0",
        "sequence": args.sequence,
        "label_source": args.label_source,
        "frame_spec": args.frames,
        "frames": frames,
        "lineage_filter": args.lineage_filter,
        "lineage_filter_rows": lineage_rows,
        "include_intensity": args.include_intensity,
        "extracted_zip_entries": extracted_entries,
        "derived_feature_rows": len(records),
        "derived_output": str(output),
        "derived_output_sha256": _sha256(output),
        "raw_file_policy": "TIFF entries were range-fetched from the ZIP archive and decoded in memory only; no raw image files are written by this script.",
    }
    if args.provenance:
        provenance_path = Path(args.provenance)
        provenance_path.parent.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "feature_rows": len(records), "output": str(output), "provenance": args.provenance}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
