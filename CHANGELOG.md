# Changelog

## 0.1.5

- Codegen emits all matching input keys per tool call (not just the first)
- MCP-oriented assert keys: repo, limit, kind, dry_run, packet_path, scope, reason

## 0.1.4

- `--anchor` codegen: emit `assert_arg_anchored` when Write quotes Read `tool_result` text
- `find_anchor_pairs`, `load_tool_result_map` for transcript pairing

## 0.1.3

- `assert_tool_input_contains` matches non-string input via `str()` (e.g. numeric `limit`)
- README: pair with pytest-mcp-contract; swamp-ops dogfood doc reference

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
