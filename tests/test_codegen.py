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
EDIT_ANCHOR_FIXTURE = Path(__file__).parent / "fixtures" / "read_edit_anchor.jsonl"
STRREPLACE_ANCHOR_FIXTURE = Path(__file__).parent / "fixtures" / "read_strreplace_anchor.jsonl"


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


def test_find_anchor_pairs_edit_new_string():
    calls = __import__(
        "session_trace.transcripts", fromlist=["load_tool_calls"]
    ).load_tool_calls(EDIT_ANCHOR_FIXTURE)
    results = load_tool_result_map(EDIT_ANCHOR_FIXTURE)
    pairs = find_anchor_pairs(calls, results)
    assert len(pairs) == 1
    assert pairs[0].write_tool == "Edit"
    assert "    return 41" in pairs[0].quoted


def test_find_anchor_pairs_strreplace_falls_back_to_old_string():
    calls = __import__(
        "session_trace.transcripts", fromlist=["load_tool_calls"]
    ).load_tool_calls(STRREPLACE_ANCHOR_FIXTURE)
    results = load_tool_result_map(STRREPLACE_ANCHOR_FIXTURE)
    pairs = find_anchor_pairs(calls, results)
    assert len(pairs) == 1
    assert pairs[0].write_tool == "StrReplace"
    assert "    return 41" in pairs[0].quoted


def test_render_test_no_order():
    src = render_test(
        [ToolCall(name="Write", input={"file_path": "a.py"})],
        emit_order=False,
    )
    assert "assert_tool_order(session_trace" not in src
    assert "assert_tool_called" in src
    compile(src, "<generated>", "exec")


def test_render_test_tools_filter():
    src = render_test(
        [
            ToolCall(name="Read", input={"file_path": "a.py"}),
            ToolCall(name="Write", input={"file_path": "src/foo.py"}),
            ToolCall(name="Bash", input={"command": "pytest"}),
        ],
        tools=frozenset({"Write"}),
    )
    assert "assert_tool_order(session_trace, ['Write'])" in src
    assert "Bash" not in src
    assert "foo.py" in src
    compile(src, "<generated>", "exec")


def test_render_test_custom_name():
    src = render_test(
        [ToolCall(name="Write", input={"file_path": "a.py"})],
        test_name="test_agent_flow",
    )
    assert "def test_agent_flow(session_trace):" in src
    compile(src, "<generated>", "exec")


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


def test_cli_test_name_flag():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "session_trace",
            str(FIXTURE),
            "--test-name",
            "test_wrote_file",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "def test_wrote_file(session_trace):" in proc.stdout
    compile(proc.stdout, "<generated>", "exec")


def test_cli_no_order_flag():
    proc = subprocess.run(
        [sys.executable, "-m", "session_trace", str(FIXTURE), "--no-order"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "assert_tool_order(session_trace" not in proc.stdout
    assert "assert_tool_called" in proc.stdout
    compile(proc.stdout, "<generated>", "exec")


def test_cli_tools_flag():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "session_trace",
            str(FIXTURE),
            "--tools",
            "Write",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Write" in proc.stdout
    assert "Read" not in proc.stdout
    compile(proc.stdout, "<generated>", "exec")
