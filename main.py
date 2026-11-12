#!/usr/bin/env python3
"""make.fun entrypoint — copy summary.txt to <MAKEFUN_OUTPUT_DIR>/entry.txt.

My design:
- stdlib only, single file, one env var (MAKEFUN_OUTPUT_DIR, default /output).
- binary-mode copy => byte-identical output, no newline mangling.
- deterministic: same source bytes in, same output bytes out, every run.
- source validated up front; distinct exit codes per failure type:
    0 = ok, 2 = source missing, 3 = source empty, 4 = write failed.
- post-write verification: output is read back and compared to the
  source before success is reported.
- prints one short status line on success.
"""

import os
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary.txt")
OUT_NAME = "entry.txt"

EXIT_OK, EXIT_NO_SOURCE, EXIT_EMPTY_SOURCE, EXIT_WRITE = 0, 2, 3, 4


def main() -> int:
    if not os.path.isfile(SOURCE):
        print(f"ERROR: source not found: {SOURCE}", file=sys.stderr)
        return EXIT_NO_SOURCE

    try:
        with open(SOURCE, "rb") as f:
            data = f.read()
    except OSError as exc:
        print(f"ERROR: cannot read {SOURCE}: {exc}", file=sys.stderr)
        return EXIT_NO_SOURCE

    if not data:
        print("ERROR: source is empty", file=sys.stderr)
        return EXIT_EMPTY_SOURCE

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_path = os.path.join(out_dir, OUT_NAME)
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
        # Integrity check: re-read and verify byte count matches source.
        with open(out_path, "rb") as f:
            written = f.read()
        if written != data:
            print("ERROR: output bytes differ from source", file=sys.stderr)
            return EXIT_WRITE
    except OSError as exc:
        print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
        return EXIT_WRITE

    print(f"OK: wrote {len(data)} chars ({len(data)} bytes) -> {out_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
