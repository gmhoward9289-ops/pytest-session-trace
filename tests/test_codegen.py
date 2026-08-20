import subprocess
import sys
from pathlib import Path

from session_trace.codegen import (
    AnchorPair,
    find_anchor_pairs,
    load_tool_result_map,
    render_test,
)
from session_trace.types import ToolCall

FIXTURE = Path(__file__).parent / "fixtures" / "one_write.jsonl"
ANCHOR_FIXTURE = Path(__file__).parent / "fixtures" / "read_write_anchor.jsonl"


def test_render_test_emits_all_input_keys_for_mcp_tool():
    src = render_test(
        [
            ToolCall(
                name="swamp_kb_search",
                input={"query": "repo visibility", "limit": 5},
            ),
        ]
    )
    assert "repo visibility" in src
    assert "'limit'" in src
    assert "'5'" in src
    compile(src, "<generated>", "exec")


def test_render_test_contains_order_and_compiles():
    src = render_test(
        [
            ToolCall(name="Read", input={"file_path": "a.py"}),
            ToolCall(name="Write", input={"file_path": "src/foo.py"}),
            ToolCall(name="Bash", input={"command": "pytest tests -v"}),
        ]
    )
    assert "assert_tool_order" in src
    assert "assert_tool_called" in src
    assert "assert_write_path" in src
    assert "assert_tool_input_contains" in src
    assert "foo.py" in src
    assert "pytest" in src
    assert "assert_arg_anchored" not in src
    compile(src, "<generated>", "exec")


def test_render_test_emits_anchor_when_pairs_given():
    pair = AnchorPair(
        read_path="src/foo.py",
        source_text="def foo():\n    return 42\n",
        quoted="return 42",
        write_tool="Write",
    )
    src = render_test(
        [
            ToolCall(name="Read", input={"file_path": "src/foo.py"}, id="r1"),
            ToolCall(name="Write", input={"file_path": "src/foo.py"}),
        ],
        anchor_pairs=[pair],
    )
    assert "assert_arg_anchored" in src
    assert "return 42" in src
    compile(src, "<generated>", "exec")


def test_find_anchor_pairs_from_jsonl():
    calls = __import__(
        "session_trace.transcripts", fromlist=["load_tool_calls"]
    ).load_tool_calls(ANCHOR_FIXTURE)
    results = load_tool_result_map(ANCHOR_FIXTURE)
    pairs = find_anchor_pairs(calls, results)
    assert len(pairs) == 1
    assert "return 42" in pairs[0].quoted


def test_cli_emits_starter_from_jsonl():
    proc = subprocess.run(
        [sys.executable, "-m", "session_trace", str(FIXTURE)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "assert_tool_order" in proc.stdout
    assert "Write" in proc.stdout
    compile(proc.stdout, "<generated>", "exec")


def test_cli_anchor_flag_emits_anchored_test():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "session_trace",
            "--anchor",
            str(ANCHOR_FIXTURE),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "assert_arg_anchored" in proc.stdout
    assert "return 42" in proc.stdout
    compile(proc.stdout, "<generated>", "exec")
