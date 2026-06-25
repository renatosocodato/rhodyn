"""Fetch a small MLCI CTC lineage subset without downloading the full archive."""

from __future__ import annotations

import argparse
import struct
import urllib.request
import zlib
from pathlib import Path


ZENODO_CTC_ZIP_URL = "https://zenodo.org/api/records/7260137/files/ctc_format.zip/content"
DEFAULT_ENTRY = "00_GT/TRA/man_track.txt"


def _content_length(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=60) as response:
        return int(response.headers["Content-Length"])


def _fetch_range(url: str, start: int, end: int) -> bytes:
    request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _central_directory(url: str, size: int) -> bytes:
    tail_len = min(262144, size)
    tail = _fetch_range(url, size - tail_len, size - 1)
    eocd_pos = tail.rfind(b"PK\x05\x06")
    if eocd_pos < 0:
        raise ValueError("could not find ZIP end-of-central-directory record")
    eocd = struct.unpack("<4sHHHHIIH", tail[eocd_pos : eocd_pos + 22])
    cd_size = eocd[5]
    cd_offset = eocd[6]
    return _fetch_range(url, cd_offset, cd_offset + cd_size - 1)


def _find_entry(central_directory: bytes, entry_name: str) -> tuple[int, int, int]:
    index = 0
    while index + 46 <= len(central_directory):
        if central_directory[index : index + 4] != b"PK\x01\x02":
            raise ValueError(f"bad central-directory signature at byte {index}")
        values = struct.unpack("<4sHHHHHHIIIHHHHHII", central_directory[index : index + 46])
        method = values[4]
        compressed_size = values[8]
        name_len = values[10]
        extra_len = values[11]
        comment_len = values[12]
        local_offset = values[16]
        name = central_directory[index + 46 : index + 46 + name_len].decode("utf-8", errors="replace")
        if name == entry_name:
            return method, compressed_size, local_offset
        index += 46 + name_len + extra_len + comment_len
    raise ValueError(f"entry not found in ZIP central directory: {entry_name}")


def _extract_entry(url: str, entry_name: str) -> bytes:
    size = _content_length(url)
    method, compressed_size, local_offset = _find_entry(_central_directory(url, size), entry_name)
    local_header = _fetch_range(url, local_offset, local_offset + 4096)
    if local_header[:4] != b"PK\x03\x04":
        raise ValueError("bad local-file header")
    values = struct.unpack("<4sHHHHHIIIHH", local_header[:30])
    name_len = values[9]
    extra_len = values[10]
    data_start = local_offset + 30 + name_len + extra_len
    compressed = _fetch_range(url, data_start, data_start + compressed_size - 1)
    if method == 0:
        return compressed
    if method == 8:
        return zlib.decompress(compressed, -15)
    raise ValueError(f"unsupported ZIP compression method: {method}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=ZENODO_CTC_ZIP_URL)
    parser.add_argument("--entry", default=DEFAULT_ENTRY)
    parser.add_argument("--max-lines", type=int, default=30)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")
    text = _extract_entry(args.url, args.entry).decode("utf-8")
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    header = [
        "# Source: Tracking one-in-a-million microbial single-cell tracking benchmark",
        "# Zenodo record: https://zenodo.org/records/7260137",
        f"# File within ctc_format.zip: {args.entry}",
        "# License: CC-BY-4.0",
        "# This is a small lineage subset for adapter tests and tutorial demonstration.",
    ]
    Path(args.output).write_text("\n".join(header + lines[: args.max_lines]) + "\n", encoding="utf-8")
    print(f"wrote {min(args.max_lines, len(lines))} lineage rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
