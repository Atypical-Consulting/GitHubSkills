# Conventions

## Naming
- Skill names: `ghs-` prefix + kebab-case (e.g., `ghs-repo-scan`)
- Directory names match skill names exactly
- Check slugs: kebab-case (e.g., `branch-protection`)
- Backlog files: `tier-{N}--{slug}.md` for health, `issue-{number}--{title-kebab}.md` for issues

## Trigger Phrases
- Include 2-4 natural trigger phrases in the skill description
- Cover common phrasings (e.g., "scan my repo", "audit my project", "run a health check")

## Status Indicators

| Indicator | Meaning | Color |
|-----------|---------|-------|
| `[PASS]` | Check passed | Green |
| `[FAIL]` | Check failed (action needed) | Red |
| `[WARN]` | Cannot verify (permissions/API) | Yellow |
| `[INFO]` | Informational (no score impact) | Blue |

## Terminal Output
- Use tables for structured data
- Progress bars: `████░░░░` (8 chars wide, filled with `█`, empty with `░`)
- Keep output scannable --- headers, spacing, alignment

## Allowed Tools

Common patterns:
- Read-only skills: `Read Glob`
- GitHub API skills: `Bash(gh:*) Read`
- Fix skills: `Bash(gh:*) Bash(git:*) Read Write Edit Glob Grep Task`

## Shared References

All shared reference docs live in `.claude/skills/shared/references/`. Skills reference them via `../shared/references/<file>.md`.

| File | Purpose |
|------|---------|
| `gh-cli-patterns.md` | Auth, repo detection, context detection, API patterns, error handling |
| `backlog-format.md` | Directory structure, file naming, metadata, tier system, scoring rules |
| `scoring-logic.md` | Tier weights, score formula, priority algorithm |
| `output-conventions.md` | Status indicators, tables, progress bars, summary blocks |
| `agent-spawning.md` | Worktree-based parallel agent patterns, context budgets |
| `implementation-workflow.md` | Repo prep, worktree mgmt, branch/commit/push/PR workflow |
| `edge-cases.md` | Rate limiting, content filters, permission errors, retries |
| `item-categories.md` | Health item classification (Category A/B/CI) and routing |
| `config.md` | Centralized scoring constants and display thresholds |
| `sync-format.md` | Sync contract: labels, issue body template, metadata |
| `agent-result-contract.md` | Universal agent JSON response format |

Other shared directories:
- Check registry: `.claude/skills/shared/checks/index.md`
- Python scripts: `.claude/skills/shared/scripts/`
- EditorConfig templates: `.claude/skills/shared/editorconfigs/`

## GSD Patterns

All skills follow structured prompt patterns:

- **XML tags** --- `<context>`, `<anti-patterns>`, `<objective>`, `<process>` wrap major sections
- **Anti-pattern tables** --- 3-column `Do NOT | Do Instead | Why` format
- **Goal-backward verification** --- Agent-spawning skills verify Existence, Substance, and Wiring of outputs
- **Cognitive bias guards** --- Diagnostic skills include bias antidote tables
- **Confidence levels** --- Classification skills indicate High/Medium/Low confidence
