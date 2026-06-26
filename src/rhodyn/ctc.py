"""Cell Tracking Challenge-style adapters for public live-cell tracking data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from math import isfinite, sqrt
from pathlib import Path
import struct
from typing import Iterable

from rhodyn.schema import TrajectoryRecord, ValidationIssue


@dataclass(frozen=True)
class CtcLineageRecord:
    """One Cell Tracking Challenge lineage row."""

    track_id: str
    start_frame: int
    end_frame: int
    parent_track_id: str


@dataclass(frozen=True)
class CtcFeatureRecord:
    """One pre-extracted object feature row from a CTC-style track."""

    track_id: str
    frame: int
    x: float
    y: float
    area: float
    intensity: float | None = None
    sequence: str = ""


@dataclass(frozen=True)
class CtcTiffImage:
    """A dependency-light grayscale TIFF image used for CTC masks or frames."""

    width: int
    height: int
    bits_per_sample: int
    pixels: tuple[int, ...]


CTC_SIGNAL_CHOICES = ("speed", "displacement", "area", "intensity")
CTC_LINEAGE_SIGNAL_CHOICES = ("presence", "track_age", "normalized_track_age", "duration")


def read_ctc_lineage(path: str | Path) -> tuple[list[CtcLineageRecord], list[ValidationIssue]]:
    """Read a CTC ``man_track.txt`` style lineage table.

    Expected whitespace-separated columns are track id, start frame, end frame,
    and parent track id. Parent id ``0`` indicates no parent in the CTC format.
    """

    records: list[CtcLineageRecord] = []
    issues: list[ValidationIssue] = []
    for row_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 4:
            issues.append(ValidationIssue(row=row_number, field="lineage", message="expected four lineage columns"))
            continue
        track_id, start, end, parent = parts
        try:
            start_frame = int(start)
            end_frame = int(end)
        except ValueError:
            issues.append(ValidationIssue(row=row_number, field="frame", message="start and end frames must be integers"))
            continue
        if end_frame < start_frame:
            issues.append(ValidationIssue(row=row_number, field="end_frame", message="end frame precedes start frame"))
        records.append(
            CtcLineageRecord(
                track_id=track_id,
                start_frame=start_frame,
                end_frame=end_frame,
                parent_track_id=parent,
            )
        )
    return records, issues


def _as_float(value: str, row: int, field: str, issues: list[ValidationIssue]) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        issues.append(ValidationIssue(row=row, field=field, message=f"expected numeric value, got {value!r}"))
        return float("nan")
    if not isfinite(parsed):
        issues.append(ValidationIssue(row=row, field=field, message=f"expected finite numeric value, got {value!r}"))
    return parsed


def _as_int(value: str, row: int, field: str, issues: list[ValidationIssue]) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        issues.append(ValidationIssue(row=row, field=field, message=f"expected integer value, got {value!r}"))
        return 0


def read_ctc_feature_csv(
    path: str | Path,
    *,
    sequence_column: str = "sequence",
    track_id_column: str = "track_id",
    frame_column: str = "frame",
    x_column: str = "x",
    y_column: str = "y",
    area_column: str = "area",
    intensity_column: str = "intensity",
) -> tuple[list[CtcFeatureRecord], list[ValidationIssue]]:
    """Read a pre-extracted CTC-style object feature table."""

    records: list[CtcFeatureRecord] = []
    issues: list[ValidationIssue] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = [track_id_column, frame_column, x_column, y_column, area_column]
        missing = [field for field in required if field not in (reader.fieldnames or [])]
        if missing:
            return [], [ValidationIssue(row=0, field=field, message="missing required CTC feature column") for field in missing]
        for row_number, row in enumerate(reader, start=2):
            track_id = (row.get(track_id_column) or "").strip()
            if not track_id:
                issues.append(ValidationIssue(row=row_number, field=track_id_column, message="empty track identifier"))
            intensity: float | None = None
            if intensity_column in (reader.fieldnames or []) and (row.get(intensity_column) or "").strip():
                intensity = _as_float(row.get(intensity_column, ""), row_number, intensity_column, issues)
            records.append(
                CtcFeatureRecord(
                    track_id=track_id,
                    frame=_as_int(row.get(frame_column, ""), row_number, frame_column, issues),
                    x=_as_float(row.get(x_column, ""), row_number, x_column, issues),
                    y=_as_float(row.get(y_column, ""), row_number, y_column, issues),
                    area=_as_float(row.get(area_column, ""), row_number, area_column, issues),
                    intensity=intensity,
                    sequence=(row.get(sequence_column) or "").strip() if sequence_column in (reader.fieldnames or []) else "",
                )
            )
    return records, issues


def _tiff_values(data: bytes, endian: str, field_type: int, count: int, value_or_offset: int) -> tuple[int, ...]:
    type_sizes = {3: 2, 4: 4}
    if field_type not in type_sizes:
        raise ValueError(f"unsupported TIFF field type: {field_type}")
    size = type_sizes[field_type] * count
    if size <= 4:
        raw = struct.pack(endian + "I", value_or_offset)[:size]
    else:
        raw = data[value_or_offset : value_or_offset + size]
    if field_type == 3:
        return struct.unpack(endian + "H" * count, raw)
    return struct.unpack(endian + "I" * count, raw)


def read_uncompressed_grayscale_tiff(data: bytes) -> CtcTiffImage:
    """Read the simple uncompressed grayscale TIFFs used by the CTC archives.

    The reader intentionally supports only the subset needed for the public
    Cell Tracking Challenge-style examples. It avoids adding an image
    dependency to the core package, while failing loudly if a TIFF uses
    compression, multiple samples per pixel, or an unsupported bit depth.
    """

    if data[:2] == b"II":
        endian = "<"
    elif data[:2] == b"MM":
        endian = ">"
    else:
        raise ValueError("unsupported TIFF byte order")
    magic, ifd_offset = struct.unpack(endian + "HI", data[2:8])
    if magic != 42:
        raise ValueError("unsupported TIFF magic number")

    entry_count = struct.unpack(endian + "H", data[ifd_offset : ifd_offset + 2])[0]
    tags: dict[int, tuple[int, int, int]] = {}
    for index in range(entry_count):
        offset = ifd_offset + 2 + index * 12
        tag, field_type, count, value_or_offset = struct.unpack(endian + "HHII", data[offset : offset + 12])
        tags[tag] = (field_type, count, value_or_offset)

    def tag_values(tag: int, default: tuple[int, ...] | None = None) -> tuple[int, ...]:
        if tag not in tags:
            if default is not None:
                return default
            raise ValueError(f"missing required TIFF tag {tag}")
        return _tiff_values(data, endian, *tags[tag])

    width = tag_values(256)[0]
    height = tag_values(257)[0]
    bits_per_sample = tag_values(258)[0]
    compression = tag_values(259, (1,))[0]
    samples_per_pixel = tag_values(277, (1,))[0]
    strip_offsets = tag_values(273)
    strip_byte_counts = tag_values(279)

    if compression != 1:
        raise ValueError("only uncompressed TIFF images are supported")
    if samples_per_pixel != 1:
        raise ValueError("only single-channel grayscale TIFF images are supported")
    if bits_per_sample not in {8, 16}:
        raise ValueError("only 8-bit and 16-bit grayscale TIFF images are supported")
    if len(strip_offsets) != len(strip_byte_counts):
        raise ValueError("TIFF strip offsets and byte counts do not match")

    pixel_bytes = b"".join(data[offset : offset + byte_count] for offset, byte_count in zip(strip_offsets, strip_byte_counts))
    expected_bytes = width * height * (bits_per_sample // 8)
    if len(pixel_bytes) != expected_bytes:
        raise ValueError("TIFF pixel byte count does not match image dimensions")
    if bits_per_sample == 8:
        pixels = tuple(pixel_bytes)
    else:
        pixels = struct.unpack(endian + "H" * (width * height), pixel_bytes)
    return CtcTiffImage(width=width, height=height, bits_per_sample=bits_per_sample, pixels=tuple(int(value) for value in pixels))


def ctc_mask_to_feature_records(
    mask: CtcTiffImage,
    *,
    frame: int,
    intensity_image: CtcTiffImage | None = None,
    allowed_track_ids: set[str] | None = None,
    sequence: str = "",
) -> list[CtcFeatureRecord]:
    """Convert one labeled CTC mask into centroid, area, and intensity rows.

    Non-zero mask labels become track identifiers. If an intensity image is
    supplied, the returned intensity is the mean raw pixel value under each
    mask label.
    """

    if intensity_image is not None and (intensity_image.width != mask.width or intensity_image.height != mask.height):
        raise ValueError("intensity image dimensions do not match the mask")

    aggregates: dict[int, list[float]] = {}
    for index, label in enumerate(mask.pixels):
        if label == 0:
            continue
        track_id = str(label)
        if allowed_track_ids is not None and track_id not in allowed_track_ids:
            continue
        x = index % mask.width
        y = index // mask.width
        if label not in aggregates:
            aggregates[label] = [0.0, 0.0, 0.0, 0.0]
        aggregates[label][0] += 1.0
        aggregates[label][1] += x
        aggregates[label][2] += y
        if intensity_image is not None:
            aggregates[label][3] += intensity_image.pixels[index]

    records: list[CtcFeatureRecord] = []
    for label, (count, x_sum, y_sum, intensity_sum) in sorted(aggregates.items()):
        intensity = None if intensity_image is None else intensity_sum / count
        records.append(
            CtcFeatureRecord(
                track_id=str(label),
                frame=frame,
                x=x_sum / count,
                y=y_sum / count,
                area=count,
                intensity=intensity,
                sequence=sequence,
            )
        )
    return records


def ctc_lineage_coverage_issues(
    features: list[CtcFeatureRecord],
    lineage: list[CtcLineageRecord],
) -> list[ValidationIssue]:
    """Check whether feature frames fall inside declared CTC lineage intervals."""

    intervals = {row.track_id: row for row in lineage}
    issues: list[ValidationIssue] = []
    for index, feature in enumerate(features, start=1):
        interval = intervals.get(feature.track_id)
        if interval is None:
            issues.append(ValidationIssue(row=index, field="track_id", message="track is absent from lineage table"))
            continue
        if feature.frame < interval.start_frame or feature.frame > interval.end_frame:
            issues.append(ValidationIssue(row=index, field="frame", message="feature frame falls outside lineage interval"))
    return issues


def _group_by_track(features: Iterable[CtcFeatureRecord]) -> dict[tuple[str, str], list[CtcFeatureRecord]]:
    grouped: dict[tuple[str, str], list[CtcFeatureRecord]] = {}
    for feature in features:
        grouped.setdefault((feature.sequence, feature.track_id), []).append(feature)
    return grouped


def _trajectory_cell_id(sequence: str, track_id: str) -> str:
    if sequence:
        return f"sequence_{sequence}_track_{track_id}"
    return f"track_{track_id}"


def _trajectory_replicate(replicate: str, sequence: str) -> str:
    if not sequence:
        return replicate
    if not replicate:
        return f"sequence_{sequence}"
    return f"{replicate}_sequence_{sequence}"


def _signal_for_track(track: list[CtcFeatureRecord], signal: str) -> list[float]:
    ordered = sorted(track, key=lambda item: item.frame)
    if signal == "area":
        return [item.area for item in ordered]
    if signal == "intensity":
        if any(item.intensity is None for item in ordered):
            raise ValueError("intensity signal requires an intensity column for every feature row")
        return [float(item.intensity) for item in ordered if item.intensity is not None]
    if signal == "displacement":
        x0 = ordered[0].x
        y0 = ordered[0].y
        return [sqrt((item.x - x0) ** 2 + (item.y - y0) ** 2) for item in ordered]
    if signal == "speed":
        speeds = [0.0]
        for previous, current in zip(ordered, ordered[1:]):
            frame_delta = current.frame - previous.frame
            if frame_delta <= 0:
                raise ValueError("speed signal requires strictly increasing frames within each track")
            distance = sqrt((current.x - previous.x) ** 2 + (current.y - previous.y) ** 2)
            speeds.append(distance / frame_delta)
        return speeds
    choices = ", ".join(CTC_SIGNAL_CHOICES)
    raise ValueError(f"unknown CTC signal {signal!r}; choices are {choices}")


def ctc_features_to_trajectory_records(
    features: list[CtcFeatureRecord],
    *,
    signal: str = "speed",
    condition: str = "mlci_tracking",
    replicate: str = "",
) -> list[TrajectoryRecord]:
    """Convert CTC-style object features into RhoDyn trajectory records."""

    if signal not in CTC_SIGNAL_CHOICES:
        choices = ", ".join(CTC_SIGNAL_CHOICES)
        raise ValueError(f"unknown CTC signal {signal!r}; choices are {choices}")
    trajectories: list[TrajectoryRecord] = []
    for (sequence, track_id), track in sorted(_group_by_track(features).items()):
        ordered = sorted(track, key=lambda item: item.frame)
        values = _signal_for_track(ordered, signal)
        for feature, value in zip(ordered, values):
            trajectories.append(
                TrajectoryRecord(
                    cell_id=_trajectory_cell_id(sequence, track_id),
                    time=float(feature.frame),
                    condition=condition,
                    signal=value,
                    replicate=_trajectory_replicate(replicate, sequence),
                )
            )
    return trajectories


def ctc_lineage_to_trajectory_records(
    lineage: list[CtcLineageRecord],
    *,
    signal: str = "normalized_track_age",
    condition: str = "mlci_tracking",
    replicate: str = "",
    max_tracks: int | None = None,
) -> list[TrajectoryRecord]:
    """Convert CTC lineage intervals into trajectory records.

    This is a lightweight public-data path for CTC archives when centroid or
    intensity features have not yet been extracted from masks. The derived
    signal describes track presence, age, normalized age, or duration rather
    than molecular activity.
    """

    if signal not in CTC_LINEAGE_SIGNAL_CHOICES:
        choices = ", ".join(CTC_LINEAGE_SIGNAL_CHOICES)
        raise ValueError(f"unknown CTC lineage signal {signal!r}; choices are {choices}")
    selected = sorted(lineage, key=lambda row: (row.start_frame, row.track_id))
    if max_tracks is not None:
        if max_tracks <= 0:
            raise ValueError("max_tracks must be positive when supplied")
        selected = selected[:max_tracks]

    records: list[TrajectoryRecord] = []
    for row in selected:
        duration = row.end_frame - row.start_frame
        length = duration + 1
        for frame in range(row.start_frame, row.end_frame + 1):
            age = frame - row.start_frame
            if signal == "presence":
                value = 1.0
            elif signal == "track_age":
                value = float(age)
            elif signal == "duration":
                value = float(length)
            else:
                value = 0.0 if duration == 0 else age / duration
            records.append(
                TrajectoryRecord(
                    cell_id=f"track_{row.track_id}",
                    time=float(frame),
                    condition=condition,
                    signal=value,
                    replicate=replicate,
                )
            )
    return records


def write_trajectory_csv(records: list[TrajectoryRecord], path: str | Path) -> None:
    """Write RhoDyn trajectory records as a tidy CSV."""

    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["cell_id", "time", "condition", "signal", "replicate"])
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "cell_id": record.cell_id,
                    "time": record.time,
                    "condition": record.condition,
                    "signal": record.signal,
                    "replicate": record.replicate,
                }
            )
