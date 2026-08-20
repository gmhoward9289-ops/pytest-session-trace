"""python -m session_trace path.jsonl > test_session.py"""

from __future__ import annotations

import sys
from pathlib import Path

from session_trace.codegen import render_test
from session_trace.transcripts import load_tool_calls


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: python -m session_trace PATH", file=sys.stderr)
        return 2
    path = Path(args[0])
    calls = load_tool_calls(path)
    sys.stdout.write(render_test(calls))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
