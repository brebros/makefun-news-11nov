#!/usr/bin/env python3
"""makefun entrypoint: copy summary.txt -> <outdir>/entry.txt verbatim.

Design notes:
- Pure stdlib, no side effects beyond the output file.
- All I/O in binary mode so the output is byte-identical to the source
  regardless of platform or locale (no newline translation).
- Paths resolved relative to this script, not the cwd, so it works
  from any invocation directory.
- Output dir: env MAKEFUN_OUTPUT_DIR if set (env var wins even when
  empty falls back via `or`), else /output; created recursively.
- Exit codes: 0 success, 1 on missing/empty source or I/O failure
  (message goes to stderr, status line to stdout).
- Idempotent/deterministic: the same source always yields the same
  bytes; running twice overwrites with identical content.
"""

import os
import sys

EXIT_OK = 0
EXIT_ERROR = 1
DEFAULT_OUT_DIR = "/output"

def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(base, "summary.txt")

    # Preflight: source must exist and be a regular file.
    if not os.path.isfile(src_path):
        sys.stderr.write(
            "ERROR: source file not found: %s\n" % src_path
        )
        return EXIT_ERROR

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUT_DIR
    out_path = os.path.join(out_dir, "entry.txt")

    try:
        with open(src_path, "rb") as f:
            payload = f.read()
    except OSError as exc:
        sys.stderr.write("ERROR: cannot read %s: %s\n" % (src_path, exc))
        return EXIT_ERROR

    # Validate: refuse to produce an empty artifact.
    if not payload:
        sys.stderr.write("ERROR: source is empty: %s\n" % src_path)
        return EXIT_ERROR


    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(payload)
        # Normalize permissions so output mode is deterministic.
        os.chmod(out_path, 0o644)
    except OSError as exc:
        sys.stderr.write(
            "ERROR: cannot write %s: %s\n" % (out_path, exc)
        )
        return EXIT_ERROR

    print("OK: wrote %d bytes to %s" % (len(payload), out_path))
    return EXIT_OK

if __name__ == "__main__":
    sys.exit(main())
