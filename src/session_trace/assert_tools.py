"""Assertions over a list of ToolCall-shaped objects (henhouse or local shim)."""

from __future__ import annotations

_WRITE_TOOLS = ("Write", "Edit")


def _names(calls) -> list[str]:
    return [c.name for c in calls]


def assert_tool_called(calls: list, name: str) -> None:
    names = _names(calls)
    if name not in names:
        raise AssertionError(f"tool {name!r} not called; actual tools: {names}")


def assert_no_tool(calls: list, name: str) -> None:
    names = _names(calls)
    if name in names:
        raise AssertionError(f"tool {name!r} was called; actual tools: {names}")


def assert_tool_order(calls: list, names: list[str]) -> None:
    """names is a subsequence of [c.name for c in calls], not necessarily adjacent."""
    actual = _names(calls)
    it = iter(actual)
    for want in names:
        for got in it:
            if got == want:
                break
        else:
            raise AssertionError(
                f"{names!r} is not a subsequence of actual tools: {actual}"
            )


def assert_write_path(calls: list, path_suffix: str) -> None:
    """A Write/Edit tool_use input.file_path endswith path_suffix."""
    actual = _names(calls)
    for call in calls:
        if call.name not in _WRITE_TOOLS:
            continue
        file_path = (call.input or {}).get("file_path")
        if isinstance(file_path, str) and file_path.endswith(path_suffix):
            return
    raise AssertionError(
        f"no Write/Edit path ending with {path_suffix!r}; actual tools: {actual}"
    )


def assert_tool_input_contains(
    calls: list, name: str, key: str, substring: str
) -> None:
    """A tool_use named name has input[key] containing substring."""
    for call in calls:
        if call.name != name:
            continue
        value = (call.input or {}).get(key)
        if value is not None and substring in str(value):
            return
    raise AssertionError(
        f"no {name!r} with {key!r} containing {substring!r}; "
        f"actual tools: {_names(calls)}"
    )
