import pytest

from session_trace.assert_tools import (
    assert_no_tool,
    assert_tool_called,
    assert_tool_order,
    assert_write_path,
)
from session_trace.types import ToolCall


def _calls():
    return [
        ToolCall(name="Read", input={"file_path": "a.py"}),
        ToolCall(name="Write", input={"file_path": "src/foo.py"}),
        ToolCall(name="Bash", input={"command": "pytest"}),
    ]


def test_called():
    assert_tool_called(_calls(), "Write")


def test_not_called():
    with pytest.raises(AssertionError, match="actual tools"):
        assert_tool_called(_calls(), "NotebookEdit")


def test_no_tool():
    assert_no_tool(_calls(), "NotebookEdit")


def test_no_tool_fails():
    with pytest.raises(AssertionError, match="actual tools"):
        assert_no_tool(_calls(), "Write")


def test_order_subsequence():
    assert_tool_order(_calls(), ["Read", "Bash"])


def test_order_not_subsequence():
    with pytest.raises(AssertionError, match="actual tools"):
        assert_tool_order(_calls(), ["Bash", "Read"])


def test_write_path():
    assert_write_path(_calls(), "foo.py")


def test_write_path_missing():
    with pytest.raises(AssertionError, match="actual tools"):
        assert_write_path(_calls(), "missing.py")


def test_tool_input_contains():
    from session_trace.assert_tools import assert_tool_input_contains

    calls = [
        ToolCall(name="Bash", input={"command": "pytest tests -v"}),
        ToolCall(name="swamp_kb_search", input={"query": "repo visibility"}),
    ]
    assert_tool_input_contains(calls, "Bash", "command", "pytest")
    assert_tool_input_contains(calls, "swamp_kb_search", "query", "visibility")
