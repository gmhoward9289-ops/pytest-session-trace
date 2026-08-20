import subprocess
import sys
from pathlib import Path

from session_trace.codegen import render_test
from session_trace.types import ToolCall

FIXTURE = Path(__file__).parent / "fixtures" / "one_write.jsonl"


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
