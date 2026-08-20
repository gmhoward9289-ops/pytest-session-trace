"""python -m session_trace path.jsonl > test_session.py"""

from __future__ import annotations

import sys
from pathlib import Path

from session_trace.codegen import render_test
from session_trace.transcripts import iter_tool_calls, read_tail


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: python -m session_trace PATH.jsonl", file=sys.stderr)
        return 2
    path = Path(args[0])
    records = read_tail(path, tail_bytes=path.stat().st_size)
    calls = iter_tool_calls(
        records,
        session_id=path.stem,
        is_subagent=path.name.startswith("agent-"),
    )
    sys.stdout.write(render_test(calls))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
