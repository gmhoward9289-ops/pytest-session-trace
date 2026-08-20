from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("fixture_name", ["one_write.jsonl", "one_write.json"])
def test_plugin_loads_fixture(pytester, fixture_name):
    src = FIXTURES / fixture_name
    dest = pytester.path / fixture_name
    dest.write_bytes(src.read_bytes())
    pytester.makepyfile(
        """
        def test_wrote(session_trace):
            from session_trace.assert_tools import assert_tool_called
            assert_tool_called(session_trace, "Write")
        """
    )
    result = pytester.runpytest("--session-trace", str(dest), "-q")
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


def test_load_tool_calls_envelope():
    from session_trace.transcripts import load_tool_calls

    calls = load_tool_calls(FIXTURES / "one_write.json")
    assert calls[0].name == "Write"
