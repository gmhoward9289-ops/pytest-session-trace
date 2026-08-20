"""python -m session_trace path.jsonl > test_session.py"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from session_trace.codegen import find_anchor_pairs, load_tool_result_map, render_test
from session_trace.transcripts import load_tool_calls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit starter pytest from a session")
    parser.add_argument("path", type=Path, help="JSONL transcript or henhouse JSON")
    parser.add_argument(
        "--anchor",
        action="store_true",
        help="emit assert_arg_anchored when Read tool_results quote Write contents",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    path = args.path
    calls = load_tool_calls(path)
    anchor_pairs = None
    if args.anchor and path.suffix.lower() == ".jsonl":
        anchor_pairs = find_anchor_pairs(calls, load_tool_result_map(path))
    sys.stdout.write(render_test(calls, anchor_pairs=anchor_pairs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
