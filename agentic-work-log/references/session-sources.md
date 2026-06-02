# Session sources

Default glob / store paths. Override with env vars from [config.md](config.md).

| Source | Env override | Location |
|--------|--------------|----------|
| Claude Code | `AGENT_DAY_CLAUDE_GLOB` | `~/.claude/projects/*/*.jsonl`, `.../subagents/*.jsonl` |
| Cursor | `AGENT_DAY_CURSOR_GLOB` | `~/.cursor/projects/*/agent-transcripts/*/*.jsonl` |
| Codex | `AGENT_DAY_CODEX_GLOB` | `~/.codex/sessions/**/*.jsonl`, `~/.codex/archived_sessions/*.jsonl` |
| OpenCode | `AGENT_DAY_OPENCODE_DB` | `~/.local/share/opencode/opencode.db` (`message` + `session`) |
| Antigravity | `AGENT_DAY_ANTIGRAVITY_GLOBS` | See below |

## Antigravity (try in order)

1. `~/.gemini/antigravity-ide/brain/*/.system_generated/logs/transcript_full.jsonl`
2. `~/.gemini/antigravity-ide/brain/*/.system_generated/logs/transcript.jsonl`
3. Legacy: `~/.gemini/antigravity/brain/...` (same layout)
4. Community CLI: `~/.antigravity-ide-cli/projects/*/*.jsonl`

Prefer `transcript_full.jsonl` when both exist.

## Custom harness

Ask the user once, then persist in config:

```json
{
  "custom_sources": [
    {
      "id": "my-agent",
      "type": "jsonl",
      "glob": "~/my-agent/logs/**/*.jsonl",
      "role_field": "role",
      "user_roles": ["user", "human"],
      "text_path": "message.content",
      "timestamp_field": "timestamp",
      "cwd_field": "cwd"
    }
  ]
}
```

For SQLite or protobuf logs, add a small adapter script under the skill directory and reference it from config (`type: "script"`, `command: ".../my-collector.py"`).

## Noise filter (all sources)

Drop prompts that:

- Start with `<system-reminder>`, `<local-command-caveat>`, tool_result wrappers
- Are slash-only with no substance (`/clear`, `/exit`, `/warmup`, `/handoff`, `/agentic-work-log`)
- Are injected `AGENTS.md` / `<INSTRUCTIONS>` system bundles
- Are empty or whitespace

Use [scripts/collect_prompts.py](../scripts/collect_prompts.py) as the canonical filter implementation.
