"""Report helpers for RhoDyn analyses."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def to_plain(value: Any) -> Any:
    """Convert dataclasses and nested containers to JSON-friendly objects."""

    if is_dataclass(value):
        return {key: to_plain(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain(item) for item in value]
    return value


def write_json_report(path: str | Path, payload: Any) -> None:
    """Write a JSON analysis report."""

    Path(path).write_text(json.dumps(to_plain(payload), indent=2) + "\n", encoding="utf-8")


def markdown_summary(title: str, rows: list[dict[str, object]]) -> str:
    """Create a compact Markdown table summary."""

    if not rows:
        return f"# {title}\n\nNo rows.\n"
    columns = list(rows[0])
    lines = [f"# {title}", "", "| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines) + "\n"

