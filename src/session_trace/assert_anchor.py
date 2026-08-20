"""Optional quote anchoring on tool arguments via trust_but_anchor.locate."""

from __future__ import annotations

from trust_but_anchor import locate


def assert_arg_anchored(source_text: str, quoted: str) -> None:
    result = locate(source_text, quoted)
    if result.get("method") == "not_found":
        raise AssertionError(
            f"quoted text not found in source: {quoted!r}"
        )
