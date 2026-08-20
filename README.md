# pytest-session-trace

Pytest plugin that turns a recorded agent session (Claude Code JSONL, henhouse `tools.v1` JSON, or legacy call list) into **deterministic tool-call assertions**. No LLM in CI. No network. No MCP SDK.

## Install

Python 3.10+. Requires [henhouse](https://github.com/gmhoward9289-ops/henhouse):

```bash
pip install git+https://github.com/gmhoward9289-ops/henhouse@v0.1.0
pip install git+https://github.com/gmhoward9289-ops/pytest-session-trace@v0.1.0
```

Develop from sibling clones under `dev/`:

```bash
pip install -e ../henhouse
pip install -e .
pytest tests -v --session-trace tests/fixtures/one_write.jsonl
```

## Example

```python
from session_trace.assert_tools import assert_tool_called, assert_tool_order

def test_wrote(session_trace):
    assert_tool_called(session_trace, "Write")
    assert_tool_order(session_trace, ["Write"])
```

Point the fixture at a transcript or henhouse envelope:

```text
pytest --session-trace path/to/session.jsonl
pytest --session-trace path/to/calls.json
# or
set SESSION_TRACE=path/to/session.jsonl
```

If neither `--session-trace` nor `SESSION_TRACE` is set, tests that request the `session_trace` fixture are **skipped** so this plugin can be installed globally without breaking unrelated suites.

## Recorders

[roost](https://github.com/gmhoward9289-ops/roost) and [leghorn](https://github.com/gmhoward9289-ops/leghorn) record and display live Claude Code sessions. This plugin only *asserts* against a saved JSONL or `python -m henhouse` output.

Parsing is delegated to [henhouse](https://github.com/gmhoward9289-ops/henhouse) (`load_tool_calls`, `ToolCall`).

Optional extra `[anchor]` uses `trust_but_anchor.locate` to fail closed when a quoted argument is not in a source file:

```text
pip install -e ".[anchor]"
```

## Starter test from a transcript

```text
python -m session_trace path/to/session.jsonl > test_session.py
```

That file is a copy-pasteable starting point, not a required CI step for this package.

## License

Apache-2.0
