"""pytest plugin: session_trace fixture from --session-trace / SESSION_TRACE."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--session-trace",
        action="store",
        default=None,
        help="Path to JSONL, henhouse.tools.v1 JSON, or legacy call list JSON.",
    )


@pytest.fixture
def session_trace(request):
    path = request.config.getoption("--session-trace") or os.environ.get(
        "SESSION_TRACE"
    )
    if not path:
        pytest.skip("no --session-trace / SESSION_TRACE")
    try:
        # Deferred so a broken or shadowed henhouse only fails tests that use
        # this fixture, instead of crashing every pytest run at plugin load.
        from session_trace.transcripts import load_tool_calls
    except ImportError as exc:
        pytest.fail(
            "pytest-session-trace could not import its 'henhouse' dependency "
            f"({exc}); a repo-local henhouse.py may be shadowing the package",
            pytrace=False,
        )
    return load_tool_calls(Path(path))
