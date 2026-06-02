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

**優先順序（嚴格依序，命中即停）：**

1. Slash：`--note=` / `--new-note` / `--team=`
2. 本輪 user 訊息：hackmd.io URL 或明確「新建」意圖
3. Env：`AGENTIC_WORK_LOG_NOTE_ID` / `AGENTIC_WORK_LOG_NOTE_URL` / `AGENTIC_WORK_LOG_NEW_NOTE`
4. Config：`hackmd_note_id`
5. 仍無目標：
   - **排程** → log `ERROR: no target note` → **exit 1**（不可自動 `--new-note`）
   - **互動** → **問一次**（URL/id 或確認 `--new-note`）；無回覆 → **exit 1**（勿默默新建）

**Config 寫回：** 僅在使用者本輪明確指定 `--note=` 或成功 `--new-note` 後，才更新 `hackmd_note_id`；不要因 config 已有 id 就覆寫使用者臨時指定的另一篇筆記。

### 解析既有筆記

```bash
../../shared/scripts/resolve-note.sh "https://hackmd.io/..."   # stdout=noteId; stderr team:PATH 若為 team URL
```

或手動：`https://hackmd.io/<noteId>` 取路徑最後一段；`@team/shortId` 用 `team-notes --output=json` + `jq`（見 `resolve-note.sh`）。

記下 `TARGET_NOTE`、`hackmd_team_path`（若有）。

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

成功後：**先** `hackmd-cli export --noteId=<id>` 驗證筆記可讀，**再** 以 temp + atomic rename 寫入 config（避免 create 成功但 config 失敗造成孤兒筆記）。回報筆記 URL。

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

與 `agent-day-review` 相同：按 `cwd` 分桶（>30 截斷）→ subagent 聚類（≤3 並行）→ 合併 trim → callout。

**超大輸入：** 若 `collect_prompts.py` 輸出 >50 則或估計原文 >30k token，先按 `cwd` 分塊各自摘要，再合併為單一 callout（map-reduce），仍受 `char_budget` 限制。

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

**插入算法（G2）：**

1. 解析筆記內所有 `## YYYY-MM-DD (ddd)`（允許僅 `## YYYY-MM-DD` 的舊格式，仍視為同日）。
2. **已有今日 heading** → 在該節內、最後一則 callout 之後（或 `<!-- agent-sync:今日 -->` 之後）append 新 callout。
3. **無今日 heading** → 找最近日期的節，在其區塊末、下一個 `##` 之前插入；若無任何日期節，在全文末追加。
4. 新日節範本：

```markdown
## YYYY-MM-DD (Mon)
<!-- agent-sync:YYYY-MM-DD -->

>[!NOTE] …
```

---

## Phase H：寫回 HackMD

遵循 [../../shared/README.md](../../shared/README.md)。

1. `export` → `/tmp/agentic-work-log-baseline.md`
2. 在 baseline 上套用 Phase G append → `/tmp/agentic-work-log-working.md`
3. 執行 safe-sync（會再 export 比對 baseline）：

```bash
REPO="<path-to-hackmd-skills-checkout>"
"$REPO/shared/scripts/safe-sync.sh" push \
  --note-id "<TARGET_NOTE>" \
  --baseline-file /tmp/agentic-work-log-baseline.md \
  --working-file /tmp/agentic-work-log-working.md \
  [--team-path "<team>"]
```

- Exit **0** → 成功；回報 `https://hackmd.io/<noteId>`
- Exit **1** → 遠端在編輯期間有變更：若 diff 僅在 `agent-sync` 區外，可將 working 合併進最新 export 後重試；若動到 agent 區塊 → **中止並請使用者決定**
- Exit **2** → CLI/參數錯誤

---

## Phase I：state

- **僅在 Phase H 成功後** 更新 `sources.*`、`last_run_iso`
- 若本輪使用者明確指定筆記或 `--new-note`，再更新 `hackmd_note_id` / `hackmd_team_path`（atomic write）

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
- `push-to-hackmd` — 通用發佈；本 skill 的 Phase H 使用 `shared/scripts/safe-sync.sh`  
- `loop` — 互動 session 內週期喚醒（非 OS 排程）

---

## 資源

- [references/config.md](references/config.md) — 筆記目的地與 env  
- [references/session-sources.md](references/session-sources.md)  
- [references/scheduling.md](references/scheduling.md)  
- [scripts/collect_prompts.py](scripts/collect_prompts.py)  
- [scripts/run-scheduled.sh](scripts/run-scheduled.sh)
- [../../shared/README.md](../../shared/README.md) — safe update 契約
