import pytest

trust_but_anchor = pytest.importorskip("trust_but_anchor")

from session_trace.assert_anchor import assert_arg_anchored


def test_arg_anchored_exact():
    assert_arg_anchored("The rain in Spain stays mainly in the plain.", "rain in Spain")


def test_arg_anchored_missing():
    with pytest.raises(AssertionError, match="not found"):
        assert_arg_anchored("The rain in Spain.", "no such quote here")
