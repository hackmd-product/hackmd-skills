# Configuration

Path: `~/.config/agentic-work-log/config.json`

## HackMD 筆記目的地

| 方式 | 範例 | 說明 |
|------|------|------|
| Slash | `/agentic-work-log --note=https://hackmd.io/abc123` | 本輪 append 到該筆記 |
| Slash | `/agentic-work-log --new-note --title="專案 A 協作"` | 新建後 append；id 寫入 config |
| 自然語言 | 「同步到這篇 https://hackmd.io/…」 | 解析 URL → note id |
| Env | `AGENTIC_WORK_LOG_NOTE_ID=abc123` | 排程預設筆記 |
| Env | `AGENTIC_WORK_LOG_NOTE_URL=https://…` | 等同 `--note` |
| Env | `AGENTIC_WORK_LOG_NEW_NOTE=1` | 排程不建議；互動可新建 |
| Config | `hackmd_note_id` | 上次成功寫入的預設筆記 |

優先順序：**slash arg > 本輪訊息 URL/新建意圖 > env > config**。

排程（cron / launchd）**必須**已有 `hackmd_note_id` 或 `AGENTIC_WORK_LOG_NOTE_ID`；缺少則失敗退出，不要自動新建。

## Schema

```json
{
  "hackmd_note_id": "abc123XYZ",
  "hackmd_team_path": null,
  "note_title": "Agentic Work Log",
  "timezone": "Asia/Taipei",
  "char_budget": 2000,
  "enabled_sources": ["claude_code", "cursor", "codex", "opencode", "antigravity"],
  "last_run_iso": "2026-06-02T12:00:00+00:00",
  "sources": {
    "claude_code": "2026-06-02T12:00:00+00:00",
    "cursor": "2026-06-02T12:00:00+00:00"
  }
}
```

| Field | Notes |
|-------|-------|
| `hackmd_note_id` | 預設 append 目標；`--note` 可覆寫並在成功後更新此欄 |
| `hackmd_team_path` | 團隊筆記時必填（`team-notes`） |
| `note_title` | 僅 `--new-note` 建立時使用（可被 `--title` 覆寫） |

## Environment variables

| Variable | Purpose |
|----------|---------|
| `AGENTIC_WORK_LOG_NOTE_ID` | 目標筆記 id |
| `AGENTIC_WORK_LOG_NOTE_URL` | 目標筆記 URL（解析後等同 NOTE_ID） |
| `AGENTIC_WORK_LOG_NEW_NOTE=1` | 強制新建 |
| `AGENTIC_WORK_LOG_TEAM` | Team path |
| `AGENTIC_WORK_LOG_TITLE` | 新建筆記標題 |
| `AGENTIC_WORK_LOG_DRY_RUN=1` | `--dry-run` |
| `AGENTIC_WORK_LOG_SINCE` | 重掃起點 |
| `AGENTIC_WORK_LOG_BUDGET` | 字數上限 |
| `AGENTIC_WORK_LOG_SOURCES` | `cursor,codex` 等 |
| `AGENTIC_WORK_LOG_RUNNER` | 排程用 harness：`cursor` / `claude` / … |

## 新建筆記範本

```bash
hackmd-cli notes create \
  --title="Agentic Work Log" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat <<'EOF'
# Agentic Work Log

由 agentic-work-log skill 增量同步。手動內容與自動區塊可並存；請勿刪除 `<!-- agent-sync:` 錨點。

EOF
)"
```

團隊筆記：`hackmd-cli team-notes create --teamPath=<team> ...`，並將 `hackmd_team_path` 寫入 config。
