"""Codegen anchor integration — Read tool_result quoted in Write contents."""

from __future__ import annotations

from pathlib import Path

import pytest

trust_but_anchor = pytest.importorskip("trust_but_anchor")

from session_trace.assert_anchor import assert_arg_anchored
from session_trace.codegen import find_anchor_pairs, load_tool_result_map
from session_trace.transcripts import load_tool_calls

FIXTURE = Path(__file__).parent / "fixtures" / "read_write_anchor.jsonl"
EDIT_FIXTURE = Path(__file__).parent / "fixtures" / "read_edit_anchor.jsonl"
STRREPLACE_FIXTURE = Path(__file__).parent / "fixtures" / "read_strreplace_anchor.jsonl"


def test_read_write_anchor_pair_from_fixture():
    calls = load_tool_calls(FIXTURE)
    pairs = find_anchor_pairs(calls, load_tool_result_map(FIXTURE))
    assert len(pairs) == 1
    assert_arg_anchored(pairs[0].source_text, pairs[0].quoted)


def test_read_edit_anchor_pair_from_fixture():
    calls = load_tool_calls(EDIT_FIXTURE)
    pairs = find_anchor_pairs(calls, load_tool_result_map(EDIT_FIXTURE))
    assert len(pairs) == 1
    assert pairs[0].write_tool == "Edit"
    assert_arg_anchored(pairs[0].source_text, pairs[0].quoted)


def test_read_strreplace_anchor_pair_from_fixture():
    calls = load_tool_calls(STRREPLACE_FIXTURE)
    pairs = find_anchor_pairs(calls, load_tool_result_map(STRREPLACE_FIXTURE))
    assert len(pairs) == 1
    assert pairs[0].write_tool == "StrReplace"
    assert_arg_anchored(pairs[0].source_text, pairs[0].quoted)
