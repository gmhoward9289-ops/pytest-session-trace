"""Codegen anchor integration — Read tool_result quoted in Write contents."""

from __future__ import annotations

from pathlib import Path

import pytest

trust_but_anchor = pytest.importorskip("trust_but_anchor")

from session_trace.assert_anchor import assert_arg_anchored
from session_trace.codegen import find_anchor_pairs, load_tool_result_map
from session_trace.transcripts import load_tool_calls

FIXTURE = Path(__file__).parent / "fixtures" / "read_write_anchor.jsonl"


def test_read_write_anchor_pair_from_fixture():
    calls = load_tool_calls(FIXTURE)
    pairs = find_anchor_pairs(calls, load_tool_result_map(FIXTURE))
    assert len(pairs) == 1
    assert_arg_anchored(pairs[0].source_text, pairs[0].quoted)
