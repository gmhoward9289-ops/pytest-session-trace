"""pytest-session-trace: recorded sessions as deterministic tool-call assertions."""

__version__ = "0.1.7"

from session_trace.assert_tools import (
    assert_no_tool,
    assert_tool_called,
    assert_tool_input_contains,
    assert_tool_order,
    assert_write_path,
)
__all__ = [
    "ToolCall",
    "assert_no_tool",
    "assert_tool_called",
    "assert_tool_input_contains",
    "assert_tool_order",
    "assert_write_path",
]


def __getattr__(name: str):
    # ToolCall comes from henhouse; resolve it lazily so importing this package
    # (which pytest does for every run via the pytest11 entry point) cannot fail
    # when a repo-local module shadows henhouse on sys.path.
    if name == "ToolCall":
        from session_trace.types import ToolCall

        return ToolCall
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
