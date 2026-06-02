---
name: agentic-work-log
description: |
  Incrementally summarizes cross-agent coding sessions (Claude Code, Cursor, Codex,
  Antigravity, OpenCode) into a HackMD work log—append to a user-chosen note or create
  a new one. Captures what was done plus pivots, no fabrication. Supports cron,
  launchd, and Windows Task Scheduler. Use for "/agentic-work-log", "agentic work log",
  "sync sessions to HackMD", "append today's agent work to this note", or scheduling
  automatic HackMD session sync from any supported agent harness.
allowed-tools: [Read, Bash, Edit, Write, Agent]
user-invocable: true
---

# Agentic Work Log

增量整理多個 agent harness 的 user prompt，**append** 到使用者指定的 HackMD 筆記（或新建一篇）。邏輯源自 `agent-day-review`；輸出目標為 HackMD，並內建排程說明。

**不取代**使用者自己的反思；只提供可核對的事實底稿（what + pivot/insight）。

---

## 與 agent-day-review 的差異

| | agent-day-review | agentic-work-log |
|--|------------------|------------------|
| 輸出 | 當週 Obsidian cycle log | 使用者指定或新建的 HackMD 筆記 |
| 寫入 | 本地 `.md` callout | `hackmd-cli` export → merge → update |
| 排程 | 文件末尾範例 | `references/scheduling.md` + `scripts/run-scheduled.sh` |
| Sources | Claude + Cursor | + Codex, OpenCode, Antigravity + 自訂 |

兩者 state **分開**：`~/.config/agentic-work-log/` vs `~/.claude/skill-state/agent-day-review/`。可同時啟用。

---

## 核心原則

1. **增量**：只處理上次 `sources.*` 之後的 prompt（見 [references/config.md](references/config.md)）。
2. **多次 trigger**：每次執行 **新建** 一個 callout，不 merge 舊 callout。
3. **嚴禁杜撰**：只寫 user prompt 字面支持的內容；寧可少不可亂。
4. **字數上限**：預設 2000 字（`AGENTIC_WORK_LOG_BUDGET` / config `char_budget`）。
5. **HackMD 不覆蓋遠端編輯**：update 前必須 export + diff（見 Phase H）。
6. **筆記目的地由使用者決定**：既有筆記 append，或明確要求時新建。

---

## 流程總覽

```
Phase 0   args / env / dry-run
Phase A1  resolve HackMD note (existing vs new)
Phase A2  load config + since timestamps
Phase B–F  collect → summarize → callout
Phase G   locate day section in note
Phase H   export → merge → update
Phase I   write state (+ persist note id if new)
```

---

## Phase 0：參數

| 輸入 | 行為 |
|------|------|
| `/agentic-work-log` | 用 config / env 中的預設筆記；若皆無且非排程 → 詢問目的地 |
| `/agentic-work-log --note=URL\|id` | append 到該筆記（本輪覆寫 config 預設，成功後可寫回 config） |
| `/agentic-work-log --new-note` | 新建個人筆記再 append（見 Phase A1） |
| `/agentic-work-log --title="…"` | 搭配 `--new-note` 的標題 |
| `/agentic-work-log --team=hackmd-design` | 團隊工作區（搭配 `--note` 或 `--new-note`） |
| `--dry-run` / `dry-run` | 只印 callout + state，**不碰 HackMD** |
| `--since=ISO` | 強制從該時間重掃 |

自然語言亦有效：「同步到 https://hackmd.io/abc123」「新建一篇叫 Agent 日誌的筆記」→ 解析為 `--note` 或 `--new-note`。

Env（排程用）：`AGENTIC_WORK_LOG_NOTE_ID`、`AGENTIC_WORK_LOG_NOTE_URL`、`AGENTIC_WORK_LOG_NEW_NOTE=1`、`AGENTIC_WORK_LOG_DRY_RUN=1`、`AGENTIC_WORK_LOG_SINCE=...`。優先順序：**slash arg > 本輪 user 訊息中的 URL/意圖 > env > config**。

`DRY_RUN` 時跳過 Phase H、I 的遠端寫入；`--new-note` 在 dry-run 只印將建立的 title，不呼叫 create。

---

## Phase A1：決定 HackMD 筆記

```
有 --note= 或訊息含 hackmd.io URL？
  yes → 解析 note id（見下）→ TARGET_NOTE
有 --new-note 或使用者明確要「新建」？
  yes → Phase A1b 建立 → TARGET_NOTE
config/env 有 hackmd_note_id？
  yes → TARGET_NOTE
排程執行且以上皆無？
  → 記錄錯誤並停止（排程不可默默新建）
互動執行且以上皆無？
  → 問一次：提供既有筆記 URL/id，或確認 --new-note
```

### 解析既有筆記

從 URL 取出 id：

- `https://hackmd.io/@team/shortId` → `hackmd-cli team-notes --teamPath=team --output=json`，對照 `shortId` 得 internal `id`
- `https://hackmd.io/<noteId>` → 路徑最後一段為 `noteId`（export 可驗證）

記下 `hackmd_note_id`、`hackmd_team_path`（若有）。

### Phase A1b：新建筆記

```bash
TITLE="${TITLE:-Agentic Work Log}"
# personal
hackmd-cli notes create \
  --title="$TITLE" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat <<'EOF'
# Agentic Work Log

由 agentic-work-log skill 增量同步。手動內容與自動區塊可並存；請勿刪除 `<!-- agent-sync:` 錨點。

EOF
)"
# team: hackmd-cli team-notes create --teamPath=... --title=... --content=...
```

成功後將 `hackmd_note_id`（與 `hackmd_team_path`）寫入 config，供下次與排程使用。

**append 到既有筆記時**：先 `export` 看一眼結構；若已有 `#` 標題與手動內容，**保留**，只在當日 `##` 區塊 append callout。

---

## Phase A2：設定與 state

```bash
CONFIG="$HOME/.config/agentic-work-log/config.json"
mkdir -p "$(dirname "$CONFIG")"
```

`since` = enabled sources 在 `sources` 的最小 timestamp；缺則 **今日 00:00 Asia/Taipei** UTC（見 [references/config.md](references/config.md)）。

---

## Phase B：收集 prompts

```bash
python3 "<skill-dir>/scripts/collect_prompts.py" \
  --since "<since_iso>" \
  --sources claude_code,cursor,codex,opencode,antigravity
```

詳見 [references/session-sources.md](references/session-sources.md)。無 prompt 時仍產生 `(本時段無實質 agent 協作)`。

---

## Phase C–F

與 `agent-day-review` 相同：按 `cwd` 分桶（>30 截斷）→ subagent 聚類（≤3 並行）→ 合併 trim → callout：

```markdown
>[!NOTE] Agent 協作回顧 (HH:MM) · {sources_label}
>
>{bullets，每行前加 `> `}
```

---

## Phase G：筆記內當日區塊

滾動日誌格式（新建筆記預設如此；既有筆記若無日節，在文末追加）：

```markdown
## 2026-06-02 (Mon)
<!-- agent-sync:2026-06-02 -->

>[!NOTE] Agent 協作回顧 (20:00) · Cursor
>…
```

```bash
hackmd-cli export --noteId=<TARGET_NOTE> > /tmp/agentic-work-log.md
```

在當日 `## YYYY-MM-DD (ddd)` 末 append callout；無該 heading 則插入新日節（見舊版 G2 規則）。

---

## Phase H：寫回 HackMD

1. `export` → baseline  
2. 套用 append → working copy  
3. 再 `export` → diff；有遠端變更則 merge  
4. `hackmd-cli notes update` 或 `team-notes update`  
5. 回報 `https://hackmd.io/<noteId>` 與「已 append / 已新建」

---

## Phase I：state

- `sources.*`、`last_run_iso`  
- 若本輪解析到穩定 `TARGET_NOTE`，更新 `hackmd_note_id` / `hackmd_team_path` 進 config

---

## 排程

[references/scheduling.md](references/scheduling.md) — **排程前**須在 config 設好 `hackmd_note_id`，或 env `AGENTIC_WORK_LOG_NOTE_ID`；不建議排程自動 `--new-note`。

`AGENTIC_WORK_LOG_RUNNER=cursor|claude|codex|opencode`

---

## 安裝

| Harness | 路徑 |
|---------|------|
| Claude Code | `~/.claude/skills/agentic-work-log/` 或 `~/.agents/skills/` |
| Cursor | `~/.cursor/skills/agentic-work-log/` |
| Codex | `~/.codex/skills/` 或 `~/.agents/skills/` |

複製整個 `agentic-work-log/` 目錄。相依：`hackmd-cli`、`python3`。

---

## 相關 skill

- `agent-day-review` — Obsidian cycle log  
- `push-to-hackmd` — HackMD auth、team、資料夾 API  
- `loop` — 互動 session 內週期喚醒（非 OS 排程）

---

## 資源

- [references/config.md](references/config.md) — 筆記目的地與 env  
- [references/session-sources.md](references/session-sources.md)  
- [references/scheduling.md](references/scheduling.md)  
- [scripts/collect_prompts.py](scripts/collect_prompts.py)  
- [scripts/run-scheduled.sh](scripts/run-scheduled.sh)
