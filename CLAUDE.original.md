# CLAUDE.md — caveman-claptrap

## README is a product artifact

The README is not documentation. It is the product's front door — the thing non-technical people read to decide if caveman is worth installing. Treat it with the same care you would treat UI copy.

**Rules for any README change:**

- Every sentence must be readable by someone who has never used an AI coding agent. If you write "SessionStart hook injects system context," that is invisible to most users — translate it.
- Keep the Before/After examples as the first thing users see. They are the entire pitch.
- The install table must always be complete and accurate. One broken install command costs a real user.
- The feature matrix (What You Get table) must stay in sync with what the code actually does. If a feature ships or is removed, update the table.
- Preserve the voice. Caveman speak in README on purpose. "Brain still big." "Cost go down forever." "One rock. That it." — this is intentional brand. Don't normalize it.
- Benchmark numbers come from real runs in `benchmarks/` and `evals/`. Never invent or round numbers. Re-run if in doubt.
- When adding a new agent to the install table, always add the corresponding detail block in the `<details>` section below it.
- Readability check before any README commit: would a non-programmer understand what this does and how to install it within 60 seconds of reading?

---

## Project overview

Caveman makes AI coding agents respond in compressed, caveman-style prose — cutting ~65-75% of output tokens while keeping full technical accuracy. It ships as a Claude Code plugin, a Codex plugin, a Gemini CLI extension, and as agent rule files for Cursor, Windsurf, Cline, Copilot, and 40+ others via `npx skills`.

---

## File structure and what owns what

### Single source of truth files — edit only these

| File | What it controls |
|------|-----------------|
| `skills/caveman-claptrap/SKILL.md` | Claptrap mode behavior built on caveman compression: intensity levels, rules, wenyan mode, auto-clarity, persistence. This is the only file to edit for behavior changes. |
| `rules/caveman-claptrap-activate.md` | The body of the always-on auto-activation rule. Injected into Cursor, Windsurf, Cline, and Copilot rule files by CI. Edit here, not in the agent-specific copies. |
| `skills/caveman-claptrap-commit/SKILL.md` | Claptrap commit message behavior. Fully independent skill. |
| `skills/caveman-claptrap-review/SKILL.md` | Claptrap code review behavior. Fully independent skill. |
| `caveman-claptrap-compress/SKILL.md` | Compress sub-skill behavior. |

### Auto-generated / auto-synced — do not edit directly

These files are overwritten by CI on every push to main that touches the sources above. Edits here will be lost.

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

`.github/workflows/sync-skill.yml` triggers on push to main when `skills/caveman-claptrap/SKILL.md` or `rules/caveman-claptrap-activate.md` changes.

What it does:
1. Copies `skills/caveman-claptrap/SKILL.md` to all agent-specific SKILL.md locations
2. Rebuilds `caveman-claptrap.skill` as a ZIP of `skills/caveman-claptrap/`
3. Rebuilds all agent rule files from `rules/caveman-claptrap-activate.md`, prepending the agent-specific frontmatter (Cursor needs `alwaysApply: true`, Windsurf needs `trigger: always_on`)
4. Commits and pushes with `[skip ci]` to avoid loops

The CI bot commits as `github-actions[bot]`. After a PR merges, wait for this workflow before declaring the release complete.

---

## Hook system (Claude Code)

Three hooks ship in `hooks/`. They communicate via a flag file at `~/.claude/.caveman-claptrap-active`.

```
SessionStart hook ──writes "full"──▶ ~/.claude/.caveman-claptrap-active ◀──writes mode── UserPromptSubmit hook
                                               │
                                            reads
                                               ▼
                                      caveman-claptrap-statusline.sh
                                     [CLAPTRAP] / [CLAPTRAP:ULTRA] / ...
```

### `hooks/caveman-claptrap-activate.js` — SessionStart hook

Runs once on every Claude Code session start. Does three things:
1. Writes the configured default mode to `~/.claude/.caveman-claptrap-active` (defaults to `full`, creates it if missing)
2. Emits the Claptrap ruleset as hidden stdout — Claude Code injects SessionStart hook stdout as system context, invisible to the user
3. Checks `~/.claude/settings.json` for an existing statusline config; if missing, appends a nudge telling Claude to offer setup on first interaction

Silent-fails on all filesystem errors — never blocks session start.

### `hooks/caveman-claptrap-mode-tracker.js` — UserPromptSubmit hook

Reads JSON from stdin (Claude Code passes prompt data as JSON on this hook event). Checks if the user prompt starts with `/claptrap` or `/caveman`. If yes, writes the detected mode to the flag file:
- `/claptrap` or `/caveman` → configured default (see `caveman-claptrap-config.js`, defaults to `full`)
- `/claptrap lite` or `/caveman lite` → `lite`
- `/claptrap ultra` or `/caveman ultra` → `ultra`
- `/claptrap wenyan` or `/caveman wenyan` or either `wenyan-full` form → `wenyan`
- `/claptrap wenyan-lite` or `/caveman wenyan-lite` → `wenyan-lite`
- `/claptrap wenyan-ultra` or `/caveman wenyan-ultra` → `wenyan-ultra`
- `/claptrap-commit` or `/caveman-commit` → `commit`
- `/claptrap-review` or `/caveman-review` → `review`
- `/claptrap:compress` or `/caveman:compress` → `compress`

Detects "stop claptrap" or "stop caveman" or "normal mode" in prompt and deletes the flag file.

### `hooks/caveman-claptrap-statusline.sh` — Statusline badge

Reads the flag file. Outputs a colored badge string for the Claude Code statusline:
- `full` or empty → `[CLAPTRAP]` (orange)
- anything else → `[CLAPTRAP:<MODE_UPPERCASED>]` (orange)

Configured in `~/.claude/settings.json` under `statusLine.command`.

### Hook installation

**Plugin install** — hooks are wired automatically by the plugin system.

**Standalone install** — `hooks/install.sh` (macOS/Linux) or `hooks/install.ps1` (Windows) copies the three hook files into `~/.claude/hooks/` and patches `~/.claude/settings.json` to register SessionStart and UserPromptSubmit hooks plus the statusline.

**Uninstall** — `hooks/uninstall.sh` / `hooks/uninstall.ps1` removes hook files and patches settings.json.

---

## Skill system

Skills are Markdown files with YAML frontmatter consumed by Claude Code's skill/plugin system and by `npx skills` for other agents.

### Intensity levels

Defined in `skills/caveman-claptrap/SKILL.md`. Six levels: `lite`, `full` (default), `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`. Level persists until changed or session ends.

### Auto-clarity rule

Caveman drops to normal prose automatically for: security warnings, irreversible action confirmations, multi-step sequences where fragment ambiguity risks misread, and when the user is confused or repeats a question. Resumes after the clear part. This is defined in the skill and must be preserved in any SKILL.md edit.

### claptrap-compress

Sub-skill in `caveman-claptrap-compress/SKILL.md`. Trigger with `/claptrap:compress` or legacy `/caveman:compress`. Takes a file path, compresses natural-language prose to caveman style, writes the compressed version to the original path, and saves a human-readable backup at `<filename>.original.md`. Validation step checks that headings, code blocks, URLs, file paths, and commands are preserved exactly. Retries up to 2 times on validation failure with targeted patches only (no full recompression). Requires Python 3.10+.

### claptrap-commit / claptrap-review

Independent skills in `skills/caveman-claptrap-commit/SKILL.md` and `skills/caveman-claptrap-review/SKILL.md`. Both have their own `description` and `name` frontmatter fields so they load independently. claptrap-commit generates Conventional Commits format with ≤50 char subject. claptrap-review outputs one-line comments in `L<line>: <severity> <problem>. <fix>.` format.

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

For agents without hook systems, the minimal always-on snippet lives in README under "Want it always on?" — keep it current with `rules/caveman-claptrap-activate.md`.

---

## Evals

`evals/` has a three-arm harness:
- `__baseline__` — no system prompt
- `__terse__` — `Answer concisely.`
- `<skill>` — `Answer concisely.\n\n{SKILL.md}`

The honest delta for any skill is **skill vs terse**, not skill vs baseline. Baseline comparison conflates the skill with generic terseness — that is cheating. The harness is designed to prevent this.

`llm_run.py` calls `claude -p --system-prompt ...` per (prompt, arm), saves output to `evals/snapshots/results.json`. `measure.py` reads the snapshot offline with tiktoken (OpenAI BPE — approximates Claude's tokenizer, ratios are meaningful, absolute numbers are approximate).

To add a skill: drop `skills/<name>/SKILL.md`. The harness auto-discovers it. To add a prompt: append a line to `evals/prompts/en.txt`.

Snapshots are committed to git. CI reads them without API calls. Only regenerate the snapshot when SKILL.md files or prompts change.

---

## Benchmarks

`benchmarks/` runs real prompts through the Claude API (not Claude Code CLI) and records raw token counts. Results are committed as JSON in `benchmarks/results/`. The benchmark table in README is generated from these results — update it when regenerating.

To reproduce: `uv run python benchmarks/run.py` (needs `ANTHROPIC_API_KEY` in `.env.local`).

---

## Key rules for agents working here

- Edit `skills/caveman-claptrap/SKILL.md` for behavior changes. Never edit synced copies.
- Edit `rules/caveman-claptrap-activate.md` for auto-activation rule changes. Never edit agent-specific rule copies.
- The README is the most important file in the repo for user-facing impact. Optimize it for non-technical readers. Preserve the caveman voice.
- Benchmark and eval numbers must be real. Never fabricate or estimate them.
- The CI workflow commits back to main after merge. Account for this when checking branch state.
- Hook files must silent-fail on all filesystem errors. Never let a hook crash block session start.
