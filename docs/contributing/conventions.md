# Conventions

## Naming
- Skill names: `ghs-` prefix + kebab-case (e.g., `ghs-repo-scan`)
- Directory names match skill names exactly
- Check slugs: kebab-case (e.g., `branch-protection`)
- GitHub Project items: health findings use `[Tier N] <check-name>` titles; issue items reference the original GitHub issue number

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
- Use stage banners from `ui-brand.md` at the start of every major phase
- Use checkpoint boxes from `ui-brand.md` before pausing for human input
- Use the defined symbol set (`✓ ✗ ⚠ ◆ ○ ⚡`) --- never random emoji

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
| `projects-format.md` | GitHub Projects item structure, field names, status values, tier system, scoring rules |
| `scoring-logic.md` | Tier weights, score formula, priority algorithm |
| `output-conventions.md` | Status indicators, tables, progress bars, summary blocks |
| `ui-brand.md` | Visual output branding: stage banners, checkpoint boxes, status symbols, routing blocks |
| `argument-parsing.md` | Standardized `$ARGUMENTS` parsing: repo detection, flags, item slugs, defaults |
| `checkpoint-patterns.md` | Typed human-in-the-loop patterns: verification, decision, action, confirmation |
| `agent-spawning.md` | Worktree-based parallel agent patterns, context budgets |
| `implementation-workflow.md` | Repo prep, worktree mgmt, branch/commit/push/PR workflow |
| `edge-cases.md` | Rate limiting, content filters, permission errors, retries |
| `item-categories.md` | Health item classification (Category A/B/CI) and routing |
| `config.md` | Centralized scoring constants and display thresholds |
| `sync-format.md` | Sync contract: labels, issue body template, metadata |
| `agent-result-contract.md` | Universal agent JSON response format |
| `gsd-integration.md` | GSD framework detection, command patterns, complexity routing |
| `state-persistence.md` | GitHub Issue-based session state across context resets |

## Shared Templates

Reusable output templates live in `.claude/skills/shared/templates/`. Skills use these for generated output (PRs, comments, issues) with `{placeholder}` variable substitution.

| Template | Used By | Purpose |
|----------|---------|---------|
| `pr-body.md` | backlog-fix, issue-implement, action-fix | PR description body |
| `analysis-comment.md` | issue-analyze | Issue analysis comment |
| `review-comment.md` | review-pr | PR review comment |
| `state-issue-body.md` | backlog-fix, orchestrate, dev-loop | State issue body |
| `sync-issue-body.md` | backlog-sync | Synced issue body |

Other shared directories:
- Check registry: `.claude/skills/shared/checks/index.md`
- EditorConfig templates: `.claude/skills/shared/editorconfigs/`

## GSD Patterns

All skills follow structured prompt patterns:

- **XML tags** --- `<context>`, `<anti-patterns>`, `<objective>`, `<process>` wrap major sections
- **Execution context** --- `<execution_context>` lists all shared reference dependencies
- **Required reading** --- `<required_reading>` declares prerequisites to load before execution
- **Anti-pattern tables** --- 3-column `Do NOT | Do Instead | Why` format
- **Rule/trigger/example triples** --- Rules state the imperative, triggers explain when, examples show concrete cases
- **Tables over prose** --- Use markdown tables for check definitions, scoring weights, routing logic, and output specs
- **Good/bad example pairs** --- Show what good output looks like and contrast with bad output
- **Goal-backward verification** --- Agent-spawning skills verify Existence, Substance, and Wiring of outputs
- **Cognitive bias guards** --- Diagnostic skills include bias antidote tables
- **Confidence levels** --- Classification skills indicate High/Medium/Low confidence
- **Progressive disclosure** --- Load indexes first, read individual items only when needed
- **Dry-run support** --- Mutation skills support `--dry-run` to show plans without executing
- **Typed checkpoints** --- Use checkpoint patterns for human-in-the-loop interactions
