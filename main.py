#!/usr/bin/env python3
"""make.fun news-summary entry builder.

Reads summary.txt from the repo root and copies it, byte for byte,
to $MAKEFUN_OUTPUT_DIR/entry.txt (default: /output).

Design goals:
- stdlib only (Python 3)
- deterministic: identical input -> byte-identical output every run.
  The whole pipeline is a single binary read + write: no timestamps,
  no text-mode newline translation, no re-encoding, no normalization.
- integrity: the output is read back and compared to the source before
  success is reported, so a silent disk error cannot pass as OK.
- fail loudly with distinct exit codes on any problem

Exit codes:
    0  success
    2  summary.txt missing / unreadable
    3  summary.txt empty
    4  write failed or read-back mismatch
"""

import os
import sys

SOURCE_NAME = "summary.txt"
OUTPUT_NAME = "entry.txt"
DEFAULT_OUTPUT_DIR = "/output"

EXIT_OK = 0
EXIT_SOURCE_MISSING = 2
EXIT_SOURCE_EMPTY = 3
EXIT_WRITE_FAILED = 4


def main() -> int:
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), SOURCE_NAME)

    if not os.path.isfile(source):
        print(f"ERROR: source not found: {source}", file=sys.stderr)
        return EXIT_SOURCE_MISSING
    try:
        with open(source, "rb") as f:
            data = f.read()
    except OSError as exc:
        print(f"ERROR: cannot read {source}: {exc}", file=sys.stderr)
        return EXIT_SOURCE_MISSING
    if not data:
        print("ERROR: source file is empty", file=sys.stderr)
        return EXIT_SOURCE_EMPTY

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
        # integrity: read back and compare bytes against source
        with open(out_path, "rb") as f:
            written = f.read()
        if written != data:
            print("ERROR: read-back mismatch, output differs from source", file=sys.stderr)
            return EXIT_WRITE_FAILED
    except OSError as exc:
        print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
        return EXIT_WRITE_FAILED

    print(f"OK: wrote {len(data)} bytes -> {out_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
