# pytest-session-trace

Pytest plugin that turns a recorded agent session (Claude Code JSONL, or henhouse JSON once that package lands) into **deterministic tool-call assertions**. No LLM in CI. No network. No MCP SDK.

Install locally:

```text
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

Point the fixture at a transcript:

```text
pytest --session-trace path/to/session.jsonl
# or
set SESSION_TRACE=path/to/session.jsonl
```

If neither `--session-trace` nor `SESSION_TRACE` is set, tests that request the `session_trace` fixture are **skipped** so this plugin can be installed globally without breaking unrelated suites.

## Recorders

[roost](https://github.com/gmhoward9289-ops/roost) and [leghorn](https://github.com/gmhoward9289-ops/leghorn) record and display live Claude Code sessions. This plugin only *asserts* against a saved JSONL.

Parser source of truth is [henhouse](https://github.com/gmhoward9289-ops/henhouse) when that package is installable (`pip install henhouse` or a path install). Until `henhouse.transcripts` is present, this repo ships a compatible Claude `tool_use` JSONL reader. `ToolCall` is imported from `henhouse.types` when available.

Optional extra `[anchor]` uses `trust_but_anchor.locate` to fail closed when a quoted argument is not in a source file:

```text
pip install -e ".[anchor]"
```

## Starter test from a transcript

```text
python -m session_trace path/to/session.jsonl > test_session.py
```

That file is a copy-pasteable starting point, not a required CI step for this package.
