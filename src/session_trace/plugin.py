"""pytest plugin: session_trace fixture from --session-trace / SESSION_TRACE."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from session_trace.transcripts import iter_tool_calls, read_tail


def pytest_addoption(parser):
    parser.addoption(
        "--session-trace",
        action="store",
        default=None,
        help="Path to a recorded agent session JSONL (or henhouse JSON).",
    )


@pytest.fixture
def session_trace(request):
    path = request.config.getoption("--session-trace") or os.environ.get(
        "SESSION_TRACE"
    )
    if not path:
        pytest.skip("no --session-trace / SESSION_TRACE")
    p = Path(path)
    records = read_tail(p, tail_bytes=p.stat().st_size)  # whole file in tests
    return iter_tool_calls(
        records, session_id=p.stem, is_subagent=p.name.startswith("agent-")
    )
