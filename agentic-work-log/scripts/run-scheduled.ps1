# Windows Task Scheduler helper for agentic-work-log
$ErrorActionPreference = 'Stop'
$LogDir = if ($env:AGENTIC_WORK_LOG_LOG_DIR) { $env:AGENTIC_WORK_LOG_LOG_DIR } else { "$env:USERPROFILE\.config\agentic-work-log\logs" }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir ("{0:yyyy-MM-dd}.log" -f (Get-Date))
$Prompt = '/agentic-work-log'
$Runner = $env:AGENTIC_WORK_LOG_RUNNER

if (-not $env:AGENTIC_WORK_LOG_NOTE_ID -and -not (Test-Path "$env:USERPROFILE\.config\agentic-work-log\config.json")) {
  "agentic-work-log: set AGENTIC_WORK_LOG_NOTE_ID or config.json" | Out-File -Append $Log
  exit 1
}

function Try-Runner($name, $cmd) {
  if ($Runner -and $Runner -ne $name) { return $false }
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { return $false }
  switch ($name) {
    'cursor' { & agent -p $Prompt *>> $Log; return $true }
    'claude' { & claude -p $Prompt *>> $Log; return $true }
    default { return $false }
  }
}

if (Try-Runner 'cursor' 'agent') { exit 0 }
if (Try-Runner 'claude' 'claude') { exit 0 }
"no runner available" | Out-File -Append $Log
exit 1
