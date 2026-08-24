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


def test_collection_survives_shadowed_henhouse(pytester):
    """A repo-local henhouse.py shadows the henhouse package when the rootdir is
    on sys.path (python -m pytest); plugin load must not crash collection."""
    pytester.makepyfile(henhouse='"""unrelated repo-local script, not the package"""\n')
    pytester.makepyfile(test_ok="def test_ok():\n    assert True\n")
    result = pytester.runpytest_subprocess("-q")
    result.assert_outcomes(passed=1)


def test_fixture_reports_shadowed_henhouse(pytester):
    pytester.makepyfile(henhouse='"""unrelated repo-local script, not the package"""\n')
    pytester.makepyfile(
        """
        def test_needs_trace(session_trace):
            assert session_trace
        """
    )
    result = pytester.runpytest_subprocess("--session-trace", "whatever.jsonl", "-q")
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*henhouse*shadowing*"])


def test_load_tool_calls_envelope():
    from session_trace.transcripts import load_tool_calls

    calls = load_tool_calls(FIXTURES / "one_write.json")
    assert calls[0].name == "Write"
