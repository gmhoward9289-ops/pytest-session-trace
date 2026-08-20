"""Emit a starter pytest file from a list of ToolCall objects."""

from __future__ import annotations

_WRITE_TOOLS = frozenset({"Write", "Edit"})
_INPUT_ASSERT_KEYS = ("query", "search", "pattern", "command")


def render_test(calls, test_name: str = "test_session") -> str:
    names = [c.name for c in calls]
    body: list[str] = []
    body.append(f"    assert_tool_order(session_trace, {names!r})")
    for name in dict.fromkeys(names):
        body.append(f"    assert_tool_called(session_trace, {name!r})")
    for call in calls:
        if call.name in _WRITE_TOOLS:
            file_path = (call.input or {}).get("file_path")
            if isinstance(file_path, str) and file_path:
                suffix = file_path.replace("\\", "/").rsplit("/", 1)[-1]
                if suffix:
                    body.append(
                        f"    assert_write_path(session_trace, {suffix!r})"
                    )
        inp = call.input or {}
        for key in _INPUT_ASSERT_KEYS:
            value = inp.get(key)
            if isinstance(value, str) and value.strip():
                snippet = value if len(value) <= 48 else value[:48]
                body.append(
                    f"    assert_tool_input_contains(session_trace, "
                    f"{call.name!r}, {key!r}, {snippet!r})"
                )
                break
    imports = (
        "from session_trace.assert_tools import (\n"
        "    assert_tool_called,\n"
        "    assert_tool_input_contains,\n"
        "    assert_tool_order,\n"
        "    assert_write_path,\n"
        ")\n\n"
    )
    lines = imports + f"def {test_name}(session_trace):\n" + "\n".join(body) + "\n"
    return lines
