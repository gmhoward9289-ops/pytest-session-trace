from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "one_write.jsonl"


def test_plugin_loads_fixture(pytester):
    pytester.makepyfile(
        """
        def test_wrote(session_trace):
            from session_trace.assert_tools import assert_tool_called
            assert_tool_called(session_trace, "Write")
        """
    )
    result = pytester.runpytest("--session-trace", str(FIXTURE), "-q")
    result.assert_outcomes(passed=1)


def test_plugin_skips_without_path(pytester):
    pytester.makepyfile(
        """
        def test_needs_trace(session_trace):
            assert session_trace
        """
    )
    result = pytester.runpytest("-q")
    result.assert_outcomes(skipped=1)
