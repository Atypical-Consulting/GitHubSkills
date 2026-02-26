# GitHubSkills — Claude Skills for GitHub Repositories

A collection of Claude Code skills for auditing, managing, and improving GitHub repositories.

## Project Structure

```
.claude/skills/                  — Skill definitions (SKILL.md files)
  shared/references/             — Shared reference docs used across skills
    gh-cli-patterns.md           — Common gh CLI patterns and error handling
    backlog-format.md            — Backlog item format and directory structure
    scoring-logic.md             — Health score calculation and tier weights
    output-conventions.md        — Terminal output formatting conventions
    agent-spawning.md            — Worktree-based parallel agent patterns
backlog/                         — Backlog items per repo (health findings + issues)
  {owner}_{repo}/
    SUMMARY.md                   — Unified repo summary
    health/                      — Health check findings
    issues/                      — Open GitHub issues
repos/                           — Local clones of target repositories (gitignored)
.gh-skills/backlog-items/        — Ideas and planned skills not yet implemented
```

## Skill Conventions

- Each skill lives in `.claude/skills/<skill-name>/SKILL.md`
- Skill names use the `ghs-` prefix with `kebab-case` (e.g., `ghs-repo-scan`)
- Directory names match the skill name exactly (e.g., `ghs-repo-scan/`)
- Skills must use the `gh` CLI for all GitHub API interactions (never raw `curl` to api.github.com)
- Skills should handle errors gracefully: 404 = missing, 403 = insufficient permissions (don't fail hard)
- Output should be clean, scannable terminal text — use tables, status indicators (`[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`), and progress bars where appropriate
- Skills should detect the current repo from `gh repo view` when no explicit repo is provided
- Follow the SKILL.md frontmatter format: `name`, `description` (with trigger phrases)

### Prompt Structure (GSD-Inspired)

Skills follow a structured prompt pattern inspired by [get-shit-done](https://github.com/gsd-build/get-shit-done):

- **Anti-Patterns section** — Explicit failure modes the agent must avoid, formatted as a table
- **Rule/trigger/example triples** — Rules state the imperative, triggers explain when it applies, examples show concrete cases
- **Tables over prose** — Use markdown tables for check definitions, scoring weights, routing logic, and output specs
- **Good/bad example pairs** — Show what good output looks like and contrast with bad output
- **Scope boundaries** — Mutation-capable skills declare what they will and won't modify
- **Circuit breakers** — Agent-spawning skills limit retry attempts (default: 3) before marking as failed
- **Context budgets** — Skills that spawn subagents document what context to pass and what to omit
- **Progressive disclosure** — Load indexes (SUMMARY.md) first, read individual items only when needed

### Shared References

Common patterns are extracted into `shared/references/` to avoid duplication. Skills reference these via `@.claude/skills/shared/references/<file>.md`:

| File | Purpose |
|------|---------|
| `gh-cli-patterns.md` | Auth checks, repo detection, issue/PR/label ops, error handling (404/403) |
| `backlog-format.md` | Directory structure, file naming, metadata fields, status values |
| `scoring-logic.md` | Tier definitions (T1=4pts, T2=2pts, T3=1pt), formula, priority algorithm |
| `output-conventions.md` | Status indicators, table patterns, progress bars, summary blocks |
| `agent-spawning.md` | Repo cloning, worktree creation, parallel execution, cleanup, context budgets |

## Available Skills

### Core Workflow (scan → sync → view → fix)

- **ghs-repo-scan** — Scan a repository for quality best practices and open issues, produce a scored report, and save all findings as structured markdown backlog items
- **ghs-backlog-board** — Show a dashboard of all backlog items (health + issues) across audited repositories with scores, progress, and next-action recommendations
- **ghs-backlog-fix** — Apply backlog item fixes using parallel worktree-based agents: clone the repo once, create worktrees, launch agents simultaneously, verify acceptance criteria, and create PRs

### Sync

- **ghs-backlog-sync** — Sync health backlog items to GitHub Issues for team visibility and tracking

### Issue Management (triage → analyze → implement)

- **ghs-issue-triage** — Verify and apply proper labels (type, priority, status) to GitHub issues
- **ghs-issue-analyze** — Deep-analyze a GitHub issue and post a structured analysis comment
- **ghs-issue-implement** — Implement a GitHub issue using worktree-based agents, then create a PR

### Actions

- **ghs-action-fix** — Fix failing GitHub Actions pipelines directly: detect broken workflows, read run logs, diagnose root causes, apply fixes in worktrees, and create PRs — no prior scan needed
- **ghs-merge-prs** — Merge open PRs (own, Renovate, or all) with CI-aware confirmation, batch support, and automatic branch cleanup

### Utilities

- **ghs-backlog-score** — Calculate and display the health score for a repository from its backlog items
- **ghs-backlog-next** — Recommend the highest-impact next item to fix across all audited repositories

## Adding New Skills

1. Create `.claude/skills/ghs-<skill-name>/SKILL.md`
2. Include frontmatter with `name: ghs-<skill-name>`, `description` (with trigger phrases), `allowed-tools`, and `compatibility`
3. Structure the body following the prompt patterns above:
   - Add an **Anti-Patterns** section with common failure modes
   - Use **rule/trigger/example triples** instead of prose paragraphs
   - Use **tables** for structured data (checks, weights, routing, output specs)
   - Include **good/bad example pairs** for output quality
   - Add a **Scope Boundary** if the skill modifies anything
   - Reference **shared files** from `shared/references/` instead of duplicating logic
4. Update the "Available Skills" list above
