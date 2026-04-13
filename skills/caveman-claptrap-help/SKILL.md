---
name: caveman-claptrap-help
description: >
  Quick-reference card for all Claptrap modes, skills, and commands.
  One-shot display, not a persistent mode. Trigger: /claptrap-help,
  /caveman-help, "claptrap help", or "what claptrap commands".
---

# Claptrap Help

Display this reference card when invoked. One-shot — do NOT change mode, write flag files, or persist anything. Output in caveman style.

## Modes

| Mode | Trigger | What change |
|------|---------|-------------|
| **Lite** | `/claptrap lite` or `/caveman lite` | Drop filler. Keep sentence structure. |
| **Full** | `/claptrap` or `/caveman` | Drop articles, filler, pleasantries, hedging. Fragments OK. Default. |
| **Ultra** | `/claptrap ultra` or `/caveman ultra` | Extreme compression. Bare fragments. Tables over prose. |
| **Wenyan-Lite** | `/claptrap wenyan-lite` or `/caveman wenyan-lite` | Classical Chinese style, light compression. |
| **Wenyan-Full** | `/claptrap wenyan` or `/caveman wenyan` | Full 文言文. Maximum classical terseness. |
| **Wenyan-Ultra** | `/claptrap wenyan-ultra` or `/caveman wenyan-ultra` | Extreme. Ancient scholar on a budget. |

Mode stick until changed or session end.

## Skills

| Skill | Trigger | What it do |
|-------|---------|-----------|
| **claptrap-commit** | `/claptrap-commit` or `/caveman-commit` | Terse commit messages. Conventional Commits. ≤50 char subject. |
| **claptrap-review** | `/claptrap-review` or `/caveman-review` | One-line PR comments: `L42: bug: user null. Add guard.` |
| **claptrap-compress** | `/claptrap:compress <file>` or `/caveman:compress <file>` | Compress .md files to caveman prose. Saves ~46% input tokens. |
| **claptrap-help** | `/claptrap-help` or `/caveman-help` | This card. |

## Deactivate

Say "stop claptrap", "stop caveman", or "normal mode". Resume anytime with `/claptrap`.

## Configure Default Mode

Default mode = `full`. Change it:

**Environment variable** (highest priority):
```bash
export CLAPTRAP_DEFAULT_MODE=ultra
```

**Config file** (`~/.config/caveman-claptrap/config.json`):
```json
{ "defaultMode": "lite" }
```

Set `"off"` to disable auto-activation on session start. User can still activate manually with `/claptrap`.

Resolution: env var > config file > `full`.

## More

Full docs: https://github.com/cashcon57/caveman-claptrap
