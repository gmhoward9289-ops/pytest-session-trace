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
        help="emit assert_arg_anchored when Read tool_results quote Write/Edit/StrReplace text",
    )
    parser.add_argument(
        "--test-name",
        default="test_session",
        help="name of the generated test function (default: test_session)",
    )
    parser.add_argument(
        "--no-order",
        action="store_true",
        help="omit assert_tool_order from generated output",
    )
    parser.add_argument(
        "--tools",
        metavar="NAME,...",
        help="comma-separated tool names to include in generated assertions",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    path = args.path
    calls = load_tool_calls(path)
    tools = None
    if args.tools:
        tools = frozenset(name.strip() for name in args.tools.split(",") if name.strip())
        if not tools:
            parser.error("--tools requires at least one tool name")

    anchor_pairs = None
    if args.anchor and path.suffix.lower() == ".jsonl":
        anchor_pairs = find_anchor_pairs(calls, load_tool_result_map(path))

    sys.stdout.write(
        render_test(
            calls,
            test_name=args.test_name,
            anchor_pairs=anchor_pairs,
            emit_order=not args.no_order,
            tools=tools,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
