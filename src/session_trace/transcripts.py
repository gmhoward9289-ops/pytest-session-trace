"""JSONL transcript readers. henhouse is the source of truth when it lands."""

from __future__ import annotations

import json
from pathlib import Path

from session_trace.types import ToolCall

try:
    from henhouse.transcripts import iter_tool_calls as iter_tool_calls
    from henhouse.transcripts import read_tail as read_tail
except ImportError:

    def read_tail(path, tail_bytes: int = 256 * 1024) -> list[dict]:
        """Whole JSON records from the last tail_bytes of a file.

        The first line of the window is dropped unless the window starts at
        byte 0 — seeking to a fixed offset lands mid-record.
        """
        path = Path(path)
        try:
            size = path.stat().st_size
            with path.open("rb") as fh:
                start = max(0, size - tail_bytes)
                fh.seek(start)
                blob = fh.read()
            lines = blob.decode("utf-8", "replace").splitlines()
        except OSError:
            return []
        if start and lines:
            lines = lines[1:]
        records = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except ValueError:
                continue
        return records

    def iter_tool_calls(
        records: list[dict],
        *,
        session_id: str | None = None,
        is_subagent: bool = False,
    ) -> list[ToolCall]:
        """Every assistant tool_use block, including Read. Order preserved."""
        calls: list[ToolCall] = []
        for rec in records:
            if rec.get("type") != "assistant":
                continue
            msg = rec.get("message") or {}
            for block in msg.get("content") or ():
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                if not isinstance(name, str) or not name:
                    continue
                inp = block.get("input")
                if not isinstance(inp, dict):
                    inp = {}
                block_id = block.get("id")
                calls.append(
                    ToolCall(
                        name=name,
                        input=inp,
                        id=block_id if isinstance(block_id, str) else None,
                        session_id=session_id,
                        source="claude",
                        is_subagent=is_subagent,
                    )
                )
        return calls
