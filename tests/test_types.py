"""ToolCall re-export from henhouse."""

from session_trace.types import ToolCall


def test_tool_call_roundtrip():
    tc = ToolCall(name="Write", input={"file_path": "a.py"}, id="t1", session_id="s1")
    d = tc.to_dict()
    assert d["name"] == "Write"
    assert d["input"]["file_path"] == "a.py"
    assert d["is_subagent"] is False
    assert d["source"] == "claude"
