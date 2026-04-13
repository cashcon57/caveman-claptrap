# CLAUDE.md — caveman-claptrap

## README is a product artifact

README = product front door. Non-technical people read it to decide if caveman worth install. Treat like UI copy.

**Rules for any README change:**

- Readable by non-AI-agent users. If you write "SessionStart hook injects system context," invisible to most — translate it.
- Keep Before/After examples first. That the pitch.
- Install table always complete + accurate. One broken install command costs real user.
- What You Get table must sync with actual code. Feature ships or removed → update table.
- Preserve voice. Caveman speak in README on purpose. "Brain still big." "Cost go down forever." "One rock. That it." — intentional brand. Don't normalize.
- Benchmark numbers from real runs in `benchmarks/` and `evals/`. Never invent or round. Re-run if doubt.
- Adding new agent to install table → add detail block in `<details>` section below.
- Readability check before any README commit: would non-programmer understand + install within 60 seconds?

---

## Project overview

Caveman makes AI coding agents respond in compressed caveman-style prose — cuts ~65-75% output tokens, full technical accuracy. Ships as Claude Code plugin, Codex plugin, Gemini CLI extension, agent rule files for Cursor, Windsurf, Cline, Copilot, 40+ others via `npx skills`.

---

## File structure and what owns what

### Single source of truth files — edit only these

| File | What it controls |
|------|-----------------|
| `skills/caveman-claptrap/SKILL.md` | Claptrap mode behavior built on caveman compression: intensity levels, rules, wenyan mode, auto-clarity, persistence. Only file to edit for behavior changes. |
| `rules/caveman-claptrap-activate.md` | Always-on auto-activation rule body. CI injects into Cursor, Windsurf, Cline, Copilot rule files. Edit here, not agent-specific copies. |
| `skills/caveman-claptrap-commit/SKILL.md` | Claptrap commit message behavior. Fully independent skill. |
| `skills/caveman-claptrap-review/SKILL.md` | Claptrap code review behavior. Fully independent skill. |
| `skills/caveman-claptrap-help/SKILL.md` | Quick-reference card. One-shot display, not a persistent mode. |
| `caveman-claptrap-compress/SKILL.md` | Compress sub-skill behavior. |

### Auto-generated / auto-synced — do not edit directly

Overwritten by CI on push to main when sources change. Edits here lost.

| File | Synced from |
|------|-------------|
| `caveman-claptrap/SKILL.md` | `skills/caveman-claptrap/SKILL.md` |
| `plugins/caveman-claptrap/skills/caveman-claptrap/SKILL.md` | `skills/caveman-claptrap/SKILL.md` |
| `.cursor/skills/caveman-claptrap/SKILL.md` | `skills/caveman-claptrap/SKILL.md` |
| `.windsurf/skills/caveman-claptrap/SKILL.md` | `skills/caveman-claptrap/SKILL.md` |
| `caveman-claptrap.skill` | ZIP of `skills/caveman-claptrap/` directory |
| `.clinerules/caveman-claptrap.md` | `rules/caveman-claptrap-activate.md` |
| `.github/copilot-instructions.md` | `rules/caveman-claptrap-activate.md` |
| `.cursor/rules/caveman-claptrap.mdc` | `rules/caveman-claptrap-activate.md` + Cursor frontmatter |
| `.windsurf/rules/caveman-claptrap.md` | `rules/caveman-claptrap-activate.md` + Windsurf frontmatter |

---

## CI sync workflow

`.github/workflows/sync-skill.yml` triggers on main push when `skills/caveman-claptrap/SKILL.md` or `rules/caveman-claptrap-activate.md` changes.

What it does:
1. Copies `skills/caveman-claptrap/SKILL.md` to all agent-specific SKILL.md locations
2. Rebuilds `caveman-claptrap.skill` as a ZIP of `skills/caveman-claptrap/`
3. Rebuilds all agent rule files from `rules/caveman-claptrap-activate.md`, prepending agent-specific frontmatter (Cursor needs `alwaysApply: true`, Windsurf needs `trigger: always_on`)
4. Commits and pushes with `[skip ci]` to avoid loops

CI bot commits as `github-actions[bot]`. After PR merge, wait for workflow before declaring release complete.

---

## Hook system (Claude Code)

Three hooks in `hooks/`. Communicate via flag file at `~/.claude/.caveman-claptrap-active`.

```
SessionStart hook ──writes "full"──▶ ~/.claude/.caveman-claptrap-active ◀──writes mode── UserPromptSubmit hook
                                               │
                                            reads
                                               ▼
                                      caveman-claptrap-statusline.sh
                                     [CLAPTRAP] / [CLAPTRAP:ULTRA] / ...
```

### `hooks/caveman-claptrap-activate.js` — SessionStart hook

Runs once per Claude Code session start. Three things:
1. Writes the configured default mode to `~/.claude/.caveman-claptrap-active` (defaults to `full`, creates if missing)
2. Emits the Claptrap ruleset as hidden stdout — Claude Code injects SessionStart hook stdout as system context, invisible to user
3. Checks `~/.claude/settings.json` for statusline config; if missing, appends nudge to offer setup on first interaction

Silent-fails on all filesystem errors — never blocks session start.

### `hooks/caveman-claptrap-mode-tracker.js` — UserPromptSubmit hook

Reads JSON from stdin. Checks if prompt starts with `/claptrap` or `/caveman`. If yes, writes mode to flag file:
- `/claptrap` or `/caveman` → configured default (see `caveman-claptrap-config.js`, defaults to `full`)
- `/claptrap lite` or `/caveman lite` → `lite`
- `/claptrap ultra` or `/caveman ultra` → `ultra`
- `/claptrap wenyan` or `/caveman wenyan` or either `wenyan-full` form → `wenyan`
- `/claptrap wenyan-lite` or `/caveman wenyan-lite` → `wenyan-lite`
- `/claptrap wenyan-ultra` or `/caveman wenyan-ultra` → `wenyan-ultra`
- `/claptrap-commit` or `/caveman-commit` → `commit`
- `/claptrap-review` or `/caveman-review` → `review`
- `/claptrap:compress` or `/caveman:compress` → `compress`

Detects "stop claptrap" or "stop caveman" or "normal mode" in prompt and deletes flag file.

### `hooks/caveman-claptrap-statusline.sh` — Statusline badge

Reads flag file. Outputs colored badge string for Claude Code statusline:
- `full` or empty → `[CLAPTRAP]` (orange)
- anything else → `[CLAPTRAP:<MODE_UPPERCASED>]` (orange)

Configured in `~/.claude/settings.json` under `statusLine.command`.

### Hook installation

**Plugin install** — hooks wired automatically by plugin system.

**Standalone install** — `hooks/install.sh` (macOS/Linux) or `hooks/install.ps1` (Windows) copies hook files into `~/.claude/hooks/` and patches `~/.claude/settings.json` to register SessionStart and UserPromptSubmit hooks plus statusline.

**Uninstall** — `hooks/uninstall.sh` / `hooks/uninstall.ps1` removes hook files and patches settings.json.

---

## Skill system

Skills = Markdown files with YAML frontmatter consumed by Claude Code's skill/plugin system and by `npx skills` for other agents.

### Intensity levels

Defined in `skills/caveman-claptrap/SKILL.md`. Six levels: `lite`, `full` (default), `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`. Persists until changed or session ends.

### Auto-clarity rule

Caveman drops to normal prose for: security warnings, irreversible action confirmations, multi-step sequences where fragment ambiguity risks misread, user confused or repeating question. Resumes after. Defined in skill — preserve in any SKILL.md edit.

### claptrap-compress

Sub-skill in `caveman-claptrap-compress/SKILL.md`. Trigger with `/claptrap:compress` or legacy `/caveman:compress`. Compresses prose to caveman style, writes to original path, saves backup at `<filename>.original.md`. Validates headings, code blocks, URLs, file paths, commands preserved. Retries up to 2 times on failure with targeted patches only. Requires Python 3.10+.

### claptrap-commit / claptrap-review

Independent skills in `skills/caveman-claptrap-commit/SKILL.md` and `skills/caveman-claptrap-review/SKILL.md`. Both have own `description` and `name` frontmatter so they load independently. claptrap-commit: Conventional Commits, ≤50 char subject. claptrap-review: one-line comments in `L<line>: <severity> <problem>. <fix>.` format.

---

## Agent distribution

How caveman reaches each agent type:

| Agent | Mechanism | Auto-activates? |
|-------|-----------|----------------|
| Claude Code | Plugin (hooks + skills) or standalone hooks | Yes — SessionStart hook injects rules |
| Codex | Plugin in `plugins/caveman-claptrap/` with `hooks.json` | Yes — SessionStart hook |
| Gemini CLI | Extension with `GEMINI.md` context file | Yes — context file loads every session |
| Cursor | `.cursor/rules/caveman-claptrap.mdc` with `alwaysApply: true` | Yes — always-on rule |
| Windsurf | `.windsurf/rules/caveman-claptrap.md` with `trigger: always_on` | Yes — always-on rule |
| Cline | `.clinerules/caveman-claptrap.md` (auto-discovered) | Yes — Cline injects all .clinerules files |
| Copilot | `.github/copilot-instructions.md` + `AGENTS.md` | Yes — repo-wide instructions |
| Others | `npx skills add cashcon57/caveman-claptrap` | No — user must say `/claptrap` each session (`/caveman` still works as alias) |

For agents without hook systems, minimal always-on snippet lives in README under "Want it always on?" — keep current with `rules/caveman-claptrap-activate.md`.

---

## Evals

`evals/` has three-arm harness:
- `__baseline__` — no system prompt
- `__terse__` — `Answer concisely.`
- `<skill>` — `Answer concisely.\n\n{SKILL.md}`

Honest delta = **skill vs terse**, not skill vs baseline. Baseline comparison conflates skill with generic terseness — that cheating. Harness designed to prevent this.

`llm_run.py` calls `claude -p --system-prompt ...` per (prompt, arm), saves to `evals/snapshots/results.json`. `measure.py` reads snapshot offline with tiktoken (OpenAI BPE — approximates Claude tokenizer, ratios meaningful, absolute numbers approximate).

Add skill: drop `skills/<name>/SKILL.md`. Harness auto-discovers. Add prompt: append line to `evals/prompts/en.txt`.

Snapshots committed to git. CI reads without API calls. Only regenerate when SKILL.md or prompts change.

---

## Benchmarks

`benchmarks/` runs real prompts through Claude API (not Claude Code CLI), records raw token counts. Results committed as JSON in `benchmarks/results/`. Benchmark table in README generated from results — update when regenerating.

To reproduce: `uv run python benchmarks/run.py` (needs `ANTHROPIC_API_KEY` in `.env.local`).

---

## Key rules for agents working here

- Edit `skills/caveman-claptrap/SKILL.md` for behavior changes. Never edit synced copies.
- Edit `rules/caveman-claptrap-activate.md` for auto-activation rule changes. Never edit agent-specific rule copies.
- README most important file for user-facing impact. Optimize for non-technical readers. Preserve caveman voice.
- Benchmark and eval numbers must be real. Never fabricate or estimate.
- CI workflow commits back to main after merge. Account for when checking branch state.
- Hook files must silent-fail on all filesystem errors. Never let hook crash block session start.
