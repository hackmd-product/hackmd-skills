# hackmd-skills

Official [HackMD](https://hackmd.io) agent skills for Claude Code, Cursor, Codex, and compatible harnesses.

Each subdirectory is a self-contained skill (with `SKILL.md`). Install by copying the folder into your harness skills directory, or clone this repo and symlink/copy individual skills.

## Skills

| Skill | Description |
|-------|-------------|
| [`agentic-work-log/`](agentic-work-log/) | Incrementally sync cross-agent session prompts into a HackMD work log (append or new note; supports scheduling). |
| [`push-to-hackmd/`](push-to-hackmd/) | Publish or back up plans, Markdown, HTML, or files to HackMD (personal or team workspace). |
| [`visualize-hmd/`](visualize-hmd/) | Turn plans and trade-offs into HTML/CSS visualizations and publish to HackMD. |

## Installation

### One skill (example: `push-to-hackmd`)

```bash
git clone https://github.com/hackmd-product/hackmd-skills.git /tmp/hackmd-skills
cp -R /tmp/hackmd-skills/push-to-hackmd ~/.cursor/skills/
# Claude Code: ~/.claude/skills/ or ~/.agents/skills/
```

### Cursor (all skills)

```bash
git clone https://github.com/hackmd-product/hackmd-skills.git /tmp/hackmd-skills
for skill in agentic-work-log push-to-hackmd visualize-hmd; do
  cp -R "/tmp/hackmd-skills/$skill" ~/.cursor/skills/
done
```

## Requirements

- [hackmd-cli](https://www.npmjs.com/package/@hackmd/hackmd-cli) (`hackmd-cli login`) for most publish flows
- **Python 3** for `agentic-work-log` collection and `visualize-hmd` build script

## Repository layout

```
hackmd-skills/
├── README.md
├── shared/                  # safe-sync, resolve-note, API reference
│   ├── README.md
│   ├── references/api.md
│   └── scripts/
├── agentic-work-log/
├── push-to-hackmd/
└── visualize-hmd/
```

Cross-skill contracts (anti-clobber updates, destination policy): [shared/README.md](shared/README.md).

## Migrating from `visualize-hmd` standalone repo

The `visualize-hmd` skill previously lived at [hackmd-product/visualize-hmd](https://github.com/hackmd-product/visualize-hmd). Use `hackmd-skills/visualize-hmd/` going forward; the standalone repo can be archived after you update local installs.

Maintained by the HackMD product team.
