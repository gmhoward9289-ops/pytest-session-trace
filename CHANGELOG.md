# Changelog

## 0.1.2

- `assert_tool_input_contains` for substring checks on tool inputs
- Richer `python -m session_trace` codegen (order, per-tool calls, write paths, query/command patterns)

## 0.1.1

- PyPI maiden release (`pip install pytest-session-trace`)
- Depends on `henhouse>=0.1.1`

## 0.1.0

- `session_trace` pytest fixture from `--session-trace` / `SESSION_TRACE`
- Tool-call assertions: `assert_tool_called`, `assert_tool_order`, `assert_no_tool`, `assert_write_path`
- Optional `[anchor]` extra via `trust-but-anchor`
- `python -m session_trace` codegen CLI
