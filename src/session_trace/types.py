"""ToolCall event type.

henhouse is the source of truth when it lands.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

try:
    from henhouse.types import ToolCall as ToolCall
except ImportError:

    @dataclass(frozen=True)
    class ToolCall:
        name: str
        input: dict[str, Any]
        id: str | None = None
        session_id: str | None = None
        source: str = "claude"  # "claude" | "cursor"
        is_subagent: bool = False

        def to_dict(self) -> dict[str, Any]:
            return asdict(self)
