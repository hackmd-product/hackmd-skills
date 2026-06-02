# Scheduling

Prerequisite: `hackmd-cli login`; **target note** set in `~/.config/agentic-work-log/config.json` (`hackmd_note_id`) or `AGENTIC_WORK_LOG_NOTE_ID`. Scheduled runs do **not** auto-create notes.

Wrapper: [scripts/run-scheduled.sh](../scripts/run-scheduled.sh) → logs under `~/.config/agentic-work-log/logs/`.

---

## macOS — launchd

`~/Library/LaunchAgents/io.hackmd.agentic-work-log.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>io.hackmd.agentic-work-log</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/ABS/PATH/TO/agentic-work-log/scripts/run-scheduled.sh</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>AGENTIC_WORK_LOG_RUNNER</key>
    <string>cursor</string>
    <key>AGENTIC_WORK_LOG_NOTE_ID</key>
    <string>YOUR_NOTE_ID</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>23</integer><key>Minute</key><integer>30</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>/Users/YOU/.config/agentic-work-log/logs/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/YOU/.config/agentic-work-log/logs/launchd.err.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/io.hackmd.agentic-work-log.plist
launchctl start io.hackmd.agentic-work-log
```

---

## Linux — cron

```cron
0 20,23 * * * AGENTIC_WORK_LOG_RUNNER=cursor AGENTIC_WORK_LOG_NOTE_ID=abc123 /bin/bash /path/to/agentic-work-log/scripts/run-scheduled.sh
```

---

## Windows — Task Scheduler

```powershell
-NoProfile -ExecutionPolicy Bypass -Command "& {
  $env:AGENTIC_WORK_LOG_RUNNER='cursor'
  $env:AGENTIC_WORK_LOG_NOTE_ID='YOUR_NOTE_ID'
  & 'C:\path\to\agentic-work-log\scripts\run-scheduled.ps1'
}"
```

---

## In-session loop

Cursor `loop` skill: `/loop 5m /agentic-work-log`（需已設定預設筆記）。IDE 關閉即停止；長期請用 OS 排程。

## Codex App

Cron automation，prompt `/agentic-work-log`；筆記 id 仍靠 config / env。
