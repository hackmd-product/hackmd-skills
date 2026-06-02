#!/usr/bin/env python3
"""Collect incremental user prompts from supported agent harnesses.

Outputs JSON: { "prompts": [ {"ts": "ISO8601Z", "cwd": "...", "source": "...", "text": "..."}, ... ] }
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Iterable

TPE = timezone(timedelta(hours=8))

NOISE_PREFIXES = (
    "<local-command-caveat>",
    "<system-reminder>",
    "<agent_skill",
    "<agent_transcripts>",
    "<rules>",
    "<user_info>",
    "<open_and_recently_viewed_files>",
)

SLASH_ONLY = re.compile(
    r"^/\s*(clear|exit|warmup|handoff|agentic-work-log|agent-day-review)\s*$",
    re.I,
)

CURSOR_TS_RE = re.compile(r"<timestamp>([^<]+)</timestamp>")
CURSOR_QUERY_RE = re.compile(r"<user_query>(.*?)</user_query>", re.DOTALL)


def parse_iso(s: str) -> datetime | None:
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def parse_cursor_ts(s: str) -> datetime | None:
    s = s.strip()
    m = re.match(r"(.+?) \(UTC([+-]\d+)\)", s)
    if not m:
        return None
    dt_part, tz_h = m.group(1), int(m.group(2))
    try:
        dt = datetime.strptime(dt_part, "%A, %b %d, %Y, %I:%M %p")
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone(timedelta(hours=tz_h))).astimezone(timezone.utc)


def is_noise(text: str) -> bool:
    t = text.strip()
    if not t or len(t) < 2:
        return True
    if any(t.startswith(p) for p in NOISE_PREFIXES):
        return True
    if SLASH_ONLY.match(t):
        return True
    if t.startswith("# AGENTS.md instructions"):
        return True
    if "<INSTRUCTIONS>" in t[:200] and "ENGINEERING" in t[:800]:
        return True
    return False


def proj_dir_to_cwd(proj_dir: str) -> str:
    if proj_dir == "subagents":
        return ""
    return "/" + proj_dir.lstrip("-").replace("-", "/")


def collect_claude(since: datetime) -> list[dict]:
    out: list[dict] = []
    patterns = [
        os.path.expanduser("~/.claude/projects/*/*.jsonl"),
        os.path.expanduser("~/.claude/projects/*/*/subagents/*.jsonl"),
    ]
    for pat in patterns:
        for fp in glob.glob(pat):
            proj_dir = os.path.basename(os.path.dirname(fp))
            if proj_dir == "subagents":
                proj_dir = os.path.basename(os.path.dirname(os.path.dirname(fp)))
            cwd = proj_dir_to_cwd(proj_dir) or fp
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts = parse_iso(o.get("timestamp", ""))
                    if not ts or ts <= since:
                        continue
                    if o.get("type") != "user":
                        continue
                    c = o.get("message", {}).get("content", "")
                    text = ""
                    if isinstance(c, list):
                        for x in c:
                            if isinstance(x, dict) and x.get("type") == "text":
                                text = x.get("text", "")
                                break
                    elif isinstance(c, str):
                        text = c
                    if is_noise(text):
                        continue
                    out.append(
                        {
                            "ts": ts.astimezone(timezone.utc).isoformat(),
                            "cwd": cwd,
                            "source": "claude_code",
                            "text": text.strip(),
                        }
                    )
    return out


def collect_cursor(since: datetime) -> list[dict]:
    out: list[dict] = []
    for fp in glob.glob(
        os.path.expanduser("~/.cursor/projects/*/agent-transcripts/*/*.jsonl")
    ):
        cwd_guess = None
        with open(fp, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for line in lines:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if o.get("role") == "assistant":
                for x in o.get("message", {}).get("content", []):
                    if isinstance(x, dict) and x.get("type") == "tool_use":
                        inp = x.get("input")
                        if isinstance(inp, dict):
                            wd = inp.get("working_directory")
                            if wd:
                                cwd_guess = wd
                                break
                if cwd_guess:
                    break
        if not cwd_guess:
            proj = fp.split("/agent-transcripts/")[0].split("/")[-1]
            cwd_guess = f"~/cursor/{proj}"
        for line in lines:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if o.get("role") != "user":
                continue
            for x in o.get("message", {}).get("content", []):
                if not (isinstance(x, dict) and x.get("type") == "text"):
                    continue
                blob = x.get("text", "")
                tm = CURSOR_TS_RE.search(blob)
                qm = CURSOR_QUERY_RE.search(blob)
                if not (tm and qm):
                    continue
                dt = parse_cursor_ts(tm.group(1))
                if not dt or dt <= since:
                    continue
                user_text = qm.group(1).strip()
                if is_noise(user_text):
                    continue
                out.append(
                    {
                        "ts": dt.astimezone(timezone.utc).isoformat(),
                        "cwd": cwd_guess,
                        "source": "cursor",
                        "text": user_text,
                    }
                )
    return out


def collect_codex(since: datetime) -> list[dict]:
    out: list[dict] = []
    patterns = [
        os.path.expanduser("~/.codex/sessions/**/*.jsonl"),
        os.path.expanduser("~/.codex/archived_sessions/*.jsonl"),
    ]
    seen_files: set[str] = set()
    for pat in patterns:
        for fp in glob.glob(pat, recursive=True):
            if fp in seen_files:
                continue
            seen_files.add(fp)
            cwd = ""
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if o.get("type") == "session_meta":
                        pl = o.get("payload") or {}
                        cwd = (pl.get("cwd") or "") if isinstance(pl, dict) else ""
                    if o.get("type") != "response_item":
                        continue
                    pl = o.get("payload") or {}
                    if not isinstance(pl, dict) or pl.get("type") != "message":
                        continue
                    if pl.get("role") != "user":
                        continue
                    ts = parse_iso(o.get("timestamp", ""))
                    if not ts or ts <= since:
                        continue
                    text = ""
                    for part in pl.get("content") or []:
                        if isinstance(part, dict) and part.get("type") == "input_text":
                            text = part.get("text", "")
                            break
                    if is_noise(text):
                        continue
                    out.append(
                        {
                            "ts": ts.astimezone(timezone.utc).isoformat(),
                            "cwd": cwd or fp,
                            "source": "codex",
                            "text": text.strip(),
                        }
                    )
    return out


def collect_opencode(since: datetime) -> list[dict]:
    db = os.path.expanduser("~/.local/share/opencode/opencode.db")
    if not os.path.isfile(db):
        return []
    out: list[dict] = []
    since_ms = int(since.timestamp() * 1000)
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            """
            SELECT m.data, s.directory
            FROM message m
            JOIN session s ON s.id = m.session_id
            WHERE m.time_created > ?
            ORDER BY m.time_created
            """,
            (since_ms,),
        ).fetchall()
    finally:
        conn.close()
    for data, session_dir in rows:
        try:
            o = json.loads(data)
        except json.JSONDecodeError:
            continue
        if o.get("role") != "user":
            continue
        ts_ms = (o.get("time") or {}).get("created")
        if not ts_ms:
            continue
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        if ts <= since:
            continue
        text = ""
        for part in o.get("parts") or []:
            if isinstance(part, dict) and part.get("type") == "text":
                text = part.get("text", "")
                break
        if not text:
            # fallback: some builds store content at top level
            text = o.get("text") or ""
        if is_noise(text):
            continue
        path = o.get("path") or {}
        cwd = (path.get("cwd") if isinstance(path, dict) else None) or session_dir or ""
        out.append(
            {
                "ts": ts.isoformat(),
                "cwd": cwd,
                "source": "opencode",
                "text": text.strip(),
            }
        )
    return out


def antigravity_globs() -> Iterable[str]:
    home = os.path.expanduser("~")
    return [
        os.path.join(home, ".gemini/antigravity-ide/brain/*/.system_generated/logs/transcript_full.jsonl"),
        os.path.join(home, ".gemini/antigravity-ide/brain/*/.system_generated/logs/transcript.jsonl"),
        os.path.join(home, ".gemini/antigravity/brain/*/.system_generated/logs/transcript_full.jsonl"),
        os.path.join(home, ".gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl"),
        os.path.join(home, ".antigravity-ide-cli/projects/*/*.jsonl"),
    ]


def collect_antigravity(since: datetime) -> list[dict]:
    out: list[dict] = []
    for pat in antigravity_globs():
        for fp in glob.glob(pat):
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    role = o.get("role") or o.get("type")
                    if role not in ("user", "human"):
                        continue
                    ts = parse_iso(
                        o.get("timestamp")
                        or o.get("created_at")
                        or o.get("time", "")
                    )
                    if not ts or ts <= since:
                        continue
                    text = o.get("text") or o.get("message") or ""
                    if isinstance(text, dict):
                        text = text.get("content") or text.get("text") or ""
                    if isinstance(text, list):
                        chunks = []
                        for x in text:
                            if isinstance(x, dict) and x.get("type") in ("text", "input_text"):
                                chunks.append(x.get("text", ""))
                        text = "\n".join(chunks)
                    if is_noise(str(text)):
                        continue
                    cwd = o.get("cwd") or fp
                    out.append(
                        {
                            "ts": ts.astimezone(timezone.utc).isoformat(),
                            "cwd": str(cwd),
                            "source": "antigravity",
                            "text": str(text).strip(),
                        }
                    )
    return out


def midnight_taipei_utc() -> datetime:
    now = datetime.now(TPE)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(timezone.utc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO timestamp (UTC); default today 00:00 Asia/Taipei")
    ap.add_argument("--sources", default="all", help="comma list or 'all'")
    args = ap.parse_args()

    since = parse_iso(args.since) if args.since else midnight_taipei_utc()
    if since is None:
        raise SystemExit(f"Invalid --since: {args.since}")

    want = set(args.sources.split(",")) if args.sources != "all" else None
    collectors = {
        "claude_code": collect_claude,
        "cursor": collect_cursor,
        "codex": collect_codex,
        "opencode": collect_opencode,
        "antigravity": collect_antigravity,
    }

    prompts: list[dict] = []
    for name, fn in collectors.items():
        if want and name not in want:
            continue
        prompts.extend(fn(since))

    prompts.sort(key=lambda x: x["ts"])
    print(json.dumps({"since": since.isoformat(), "prompts": prompts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
