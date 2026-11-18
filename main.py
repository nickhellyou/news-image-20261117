#!/usr/bin/env python3
"""Validate the bundled entry image and place a copy in the output folder.

The program reads ``entry.png`` sitting next to this script, checks that it
really is a PNG file, and writes an identical copy into the directory named
by ``MAKEFUN_OUTPUT_DIR`` (``/output`` when the variable is unset).
"""

import hashlib
import os
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IMAGE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"
MAX_IMAGE_BYTES = 1_048_576  # 1 MiB; entry images are expected to stay below this


def abort(message):
    """Print an error to stderr and stop with a non-zero exit code."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_source_image(script_dir):
    """Return the raw bytes of entry.png, or stop if it is missing/invalid."""
    source = script_dir / IMAGE_NAME
    if not source.is_file():
        abort(f"missing input image: {source}")

    payload = source.read_bytes()
    if len(payload) > MAX_IMAGE_BYTES:
        abort(
            f"input image too large: {len(payload)} bytes "
            f"(max {MAX_IMAGE_BYTES} bytes)"
        )
    if payload[: len(PNG_SIGNATURE)] != PNG_SIGNATURE:
        abort("input is not a PNG file (bad magic bytes)")
    return source, payload


def main():
    script_dir = Path(__file__).resolve().parent
    source, payload = load_source_image(script_dir)

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    target = out_dir / IMAGE_NAME
    target.write_bytes(payload)

    digest = hashlib.sha256(payload).hexdigest()
    print(f"wrote {target}")
    print(f"sha256: {digest}")
    print(f"bytes: {len(payload)}")


if __name__ == "__main__":
    main()
