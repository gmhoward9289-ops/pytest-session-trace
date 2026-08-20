# pytest-session-trace

[![Discussions](https://img.shields.io/github/discussions/gmhoward9289-ops/pytest-session-trace)](https://github.com/gmhoward9289-ops/pytest-session-trace/discussions)

Pytest plugin that turns a recorded agent session (Claude Code JSONL, henhouse `tools.v1` JSON, or legacy call list) into **deterministic tool-call assertions**. No LLM in CI. No network. No MCP SDK.

## Install

Python 3.10+. Requires [henhouse](https://github.com/gmhoward9289-ops/henhouse):

```bash
pip install henhouse pytest-session-trace
```

Or install tagged releases from GitHub:

```bash
pip install git+https://github.com/gmhoward9289-ops/henhouse@v0.1.2
pip install git+https://github.com/gmhoward9289-ops/pytest-session-trace@v0.1.7
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

Pair with [pytest-mcp-contract](https://github.com/gmhoward9289-ops/pytest-mcp-contract) in the same repo: that plugin asserts the MCP server registers the right tools, read-only annotations, and input JSON schemas; this plugin asserts a saved session actually called them. Public starter: [`pytest-mcp-contract/examples/proof_stack/`](https://github.com/gmhoward9289-ops/pytest-mcp-contract/tree/main/examples/proof_stack). swamp-ops `docs/SESSION_TRACE.md` documents the private dogfood pattern.

`python -m session_trace` codegen emits `assert_tool_input_contains` for MCP args (`query`, `repo`, `limit`, …) as well as editor tools.

Optional extra `[anchor]` uses `trust_but_anchor.locate` to fail closed when a quoted argument is not in a source file:

```text
pip install -e ".[anchor]"
```

## Starter test from a transcript

```text
python -m session_trace path/to/session.jsonl > test_session.py
python -m session_trace --anchor path/to/session.jsonl > test_session.py
python -m session_trace path/to/session.jsonl --test-name test_agent_flow --tools Write,Read
python -m session_trace path/to/session.jsonl --no-order --tools swamp_estate_status
```

With `--anchor`, codegen emits `assert_arg_anchored` when Write/Edit/StrReplace text
quotes a prior Read `tool_result` in the JSONL (requires `[anchor]` extra). Supported
write shapes: Write `contents`; Edit `new_string`, `contents`, or `old_string`; StrReplace
`new_string` (preferred) or `old_string`.

| Flag | Effect |
| --- | --- |
| `--test-name NAME` | Generated test function name (default `test_session`) |
| `--no-order` | Omit `assert_tool_order` |
| `--tools NAME,...` | Only emit assertions for listed tools |

That file is a copy-pasteable starting point, not a required CI step for this package.

Have a recorded session and a pytest file that pins it? Post the workflow in [Show and tell](https://github.com/gmhoward9289-ops/pytest-session-trace/discussions/categories/show-and-tell).

## License

Apache-2.0
