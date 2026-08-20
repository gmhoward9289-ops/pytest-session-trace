"""Generated --anchor test runs clean under pytest with the source fixture."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("trust_but_anchor")

FIXTURE = Path(__file__).parent / "fixtures" / "read_write_anchor.jsonl"


def test_codegen_anchor_output_passes_pytest(pytester):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "session_trace",
            "--anchor",
            str(FIXTURE),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    test_path = pytester.path / "test_generated_from_anchor_codegen.py"
    test_path.write_text(proc.stdout, encoding="utf-8")
    result = pytester.runpytest(
        str(test_path),
        f"--session-trace={FIXTURE}",
        "-q",
    )
    result.assert_outcomes(passed=1)
