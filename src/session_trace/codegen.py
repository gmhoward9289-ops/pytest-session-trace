"""Emit a starter pytest file from a list of ToolCall objects."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_WRITE_TOOLS = frozenset({"Write", "Edit"})
_READ_TOOLS = frozenset({"Read"})
_INPUT_ASSERT_KEYS = (
    "query",
    "search",
    "pattern",
    "command",
    # MCP / swamp-ops tool args
    "repo",
    "limit",
    "kind",
    "dry_run",
    "packet_path",
    "scope",
    "reason",
)
_MIN_ANCHOR_LEN = 12
_MAX_SOURCE_CHARS = 4000


@dataclass(frozen=True)
class AnchorPair:
    """Read tool_result text and a Write/Edit substring that appears in it."""

    read_path: str
    source_text: str
    quoted: str
    write_tool: str


def _tool_use_blocks(record: dict) -> list[dict]:
    if record.get("type") != "assistant":
        return []
    message = record.get("message") or {}
    content = message.get("content")
    if not isinstance(content, list):
        return []
    blocks: list[dict] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            blocks.append(block)
    return blocks


def _tool_result_text(record: dict) -> tuple[str, str] | None:
    if record.get("type") != "user":
        return None
    message = record.get("message") or {}
    content = message.get("content")
    if not isinstance(content, list):
        return None
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_result":
            continue
        tool_use_id = block.get("tool_use_id")
        raw = block.get("content")
        if tool_use_id and isinstance(raw, str):
            return tool_use_id, raw
    return None


def load_tool_result_map(path: Path) -> dict[str, str]:
    """Map tool_use_id → tool_result text from a JSONL transcript."""
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            pair = _tool_result_text(record)
            if pair is not None:
                mapping[pair[0]] = pair[1]
    return mapping


def _find_quote(source: str, written: str) -> str | None:
    if not source or not written:
        return None
    limit = min(len(written), 200)
    for length in range(limit, _MIN_ANCHOR_LEN - 1, -1):
        for start in range(len(written) - length + 1):
            snippet = written[start : start + length]
            if snippet in source:
                return snippet
    return None


def find_anchor_pairs(calls, tool_results: dict[str, str]) -> list[AnchorPair]:
    """Pair Read tool_results with later Write/Edit contents that quote them."""
    pairs: list[AnchorPair] = []
    read_sources: list[tuple[str, str]] = []

    for call in calls:
        if call.name in _READ_TOOLS:
            tool_id = call.id
            file_path = (call.input or {}).get("file_path")
            if not isinstance(file_path, str):
                continue
            if tool_id and tool_id in tool_results:
                read_sources.append((file_path, tool_results[tool_id]))
        elif call.name in _WRITE_TOOLS:
            contents = (call.input or {}).get("contents")
            if not isinstance(contents, str):
                continue
            for read_path, source in read_sources:
                quoted = _find_quote(source, contents)
                if quoted:
                    pairs.append(
                        AnchorPair(
                            read_path=read_path,
                            source_text=source,
                            quoted=quoted,
                            write_tool=call.name,
                        )
                    )
                    break
    return pairs


def _escape_triple(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'''", "\\'''")


def render_test(
    calls,
    test_name: str = "test_session",
    *,
    anchor_pairs: list[AnchorPair] | None = None,
) -> str:
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
            if value is None:
                continue
            text = str(value).strip()
            if not text:
                continue
            snippet = text if len(text) <= 48 else text[:48]
            body.append(
                f"    assert_tool_input_contains(session_trace, "
                f"{call.name!r}, {key!r}, {snippet!r})"
            )

    if anchor_pairs:
        for index, pair in enumerate(anchor_pairs):
            source = pair.source_text
            if len(source) > _MAX_SOURCE_CHARS:
                source = source[:_MAX_SOURCE_CHARS]
            var = f"READ_SOURCE_{index}"
            body.append(f"    {var} = '''{_escape_triple(source)}'''")
            body.append(f"    assert_arg_anchored({var}, {pair.quoted!r})")

    imports = (
        "from session_trace.assert_tools import (\n"
        "    assert_tool_called,\n"
        "    assert_tool_input_contains,\n"
        "    assert_tool_order,\n"
        "    assert_write_path,\n"
        ")\n"
    )
    if anchor_pairs:
        imports += (
            "from session_trace.assert_anchor import assert_arg_anchored\n"
            "  # requires: pip install pytest-session-trace[anchor]\n\n"
        )
    else:
        imports += "\n"

    lines = imports + f"def {test_name}(session_trace):\n" + "\n".join(body) + "\n"
    return lines
