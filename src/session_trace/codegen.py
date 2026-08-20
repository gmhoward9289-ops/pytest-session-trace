"""Emit a starter pytest file from a list of ToolCall objects."""

from __future__ import annotations


def render_test(calls, test_name: str = "test_session") -> str:
    names = [c.name for c in calls]
    return (
        "from session_trace.assert_tools import assert_tool_order, assert_tool_called\n\n"
        f"def {test_name}(session_trace):\n"
        f"    assert_tool_order(session_trace, {names!r})\n"
    )
