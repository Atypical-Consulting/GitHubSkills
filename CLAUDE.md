# GitHubSkills — Claude Skills for GitHub Repositories

A collection of Claude Code skills for auditing, managing, and improving GitHub repositories.

## Project Structure

```
.claude/skills/                  — Skill definitions (SKILL.md files)
  shared/references/             — Shared reference docs used across skills
    gh-cli-patterns.md           — gh CLI patterns, auth, repo detection, context, edge cases
    backlog-format.md            — Backlog directory structure, file naming, metadata, scoring
    scoring-logic.md             — Health score calculation and tier weights
    output-conventions.md        — Terminal output formatting conventions
    agent-spawning.md            — Worktree-based parallel agent patterns
    implementation-workflow.md   — Repo clone/pull, worktree mgmt, branch/commit/push/PR
    edge-cases.md                — Rate limiting, content filters, permission errors, retries
    item-categories.md           — Health item classification (Category A/B/CI) and routing
    config.md                    — Centralized scoring constants and display thresholds
    sync-format.md               — Sync contract: labels, issue body template, metadata
    agent-result-contract.md     — Universal agent JSON response format
    gsd-integration.md           — GSD framework detection, command patterns, complexity routing
    state-persistence.md         — STATE.md pattern for session state across context resets
backlog/                         — Backlog items per repo (health findings + issues)
  {owner}_{repo}/
    SUMMARY.md                   — Unified repo summary
    STATE.md                     — Session state: decisions, blockers, history (optional)
    health/                      — Health check findings
    issues/                      — Open GitHub issues
.planning/                       — Refactoring roadmap and project-level planning
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

- **XML tag structure** — All skills use `<context>`, `<anti-patterns>`, `<objective>`, `<process>` tags; `<rules>` and `<examples>` where applicable
- **Anti-Patterns table** — 3-column `Do NOT | Do Instead | Why` table inside `<anti-patterns>` tags
- **Rule/trigger/example triples** — Rules state the imperative, triggers explain when it applies, examples show concrete cases
- **Tables over prose** — Use markdown tables for check definitions, scoring weights, routing logic, and output specs
- **Good/bad example pairs** — Show what good output looks like and contrast with bad output
- **Scope boundaries** — Mutation-capable skills declare what they will and won't modify
- **Circuit breakers** — Agent-spawning skills limit retry attempts (default: 3) before marking as failed
- **Context budgets** — Skills that spawn subagents document what context to pass and what to omit
- **Goal-backward verification** — Agent-spawning skills verify Existence, Substance, and Wiring of outputs
- **Cognitive bias guards** — Diagnostic skills include bias antidote tables
- **Confidence levels** — Classification/diagnostic skills indicate High/Medium/Low confidence
- **Progressive disclosure** — Load indexes (SUMMARY.md) first, read individual items only when needed

### Shared References

Common patterns are extracted into `shared/references/` to avoid duplication. Skills reference these via `../shared/references/<file>.md` (relative from skill directory):

| File | Purpose |
|------|---------|
| `gh-cli-patterns.md` | Auth, repo detection, context detection, issue/PR/label ops, error handling, edge cases |
| `backlog-format.md` | Directory structure, file naming, metadata fields, tier system, scoring rules, status values |
| `scoring-logic.md` | Tier definitions (T1=4pts, T2=2pts, T3=1pt), formula, priority algorithm |
| `output-conventions.md` | Status indicators, table patterns, progress bars, summary blocks |
| `agent-spawning.md` | Repo cloning, worktree creation, parallel execution, cleanup, context budgets |
| `implementation-workflow.md` | Repo prep, worktree mgmt, branch/commit/push/PR workflow, pre-flight checks |
| `edge-cases.md` | Rate limiting, content filters, permission errors, bounded retries |
| `item-categories.md` | Health item classification (Category A/B/CI) and routing rules |
| `config.md` | Centralized scoring constants, display thresholds, status indicators |
| `sync-format.md` | Label taxonomy, issue title convention, body template, hidden metadata comment |
| `agent-result-contract.md` | Universal agent JSON response format, status semantics, health check variant |
| `gsd-integration.md` | GSD detection, complexity routing (fast path vs GSD pipeline), command patterns, context handoff |
| `state-persistence.md` | STATE.md lifecycle, format, reading/writing state, session history, blocker tracking |

## Available Skills

### Core Workflow (scan → sync → view → fix)

- **ghs-repo-scan** — Scan a repository for quality best practices and open issues, produce a scored report, and save all findings as structured markdown backlog items
- **ghs-backlog-board** — Show a dashboard of all backlog items (health + issues) across audited repositories with scores, progress, and next-action recommendations
- **ghs-backlog-fix** — Apply backlog item fixes using parallel worktree-based agents: clone the repo once, create worktrees, launch agents simultaneously, verify acceptance criteria, and create PRs

### Sync

- **ghs-backlog-sync** — Sync health backlog items to GitHub Issues for team visibility and tracking

### Profile

- **ghs-profile** — Display a full 360-degree view of a GitHub user: profile, repos, contributions, open work, orgs, and activity

### Issue Management (triage → analyze → implement)

- **ghs-issue-triage** — Verify and apply proper labels (type, priority, status) to GitHub issues
- **ghs-issue-analyze** — Deep-analyze a GitHub issue and post a structured analysis comment
- **ghs-issue-implement** — Implement a GitHub issue using worktree-based agents, then create a PR

### Code Review & Release

- **ghs-review-pr** — Review a GitHub PR: fetch diff, analyze for correctness/security/performance/style/tests, post structured review comment with findings by severity
- **ghs-release** — Create a GitHub Release with auto-generated changelog from conventional commits, semver version bump, dry-run and pre-release support

### Repository Setup

- **ghs-project-init** — Scaffold a new GitHub repository with all quality essentials for a 100% health score, using GSD for multi-file scaffolding with tech-stack-tailored templates

### Actions

- **ghs-action-fix** — Fix failing GitHub Actions pipelines directly: detect broken workflows, read run logs, diagnose root causes, apply fixes in worktrees, and create PRs — no prior scan needed
- **ghs-merge-prs** — Merge open PRs (own, Renovate, or all) with CI-aware confirmation, batch support, and automatic branch cleanup

### Orchestration

- **ghs-orchestrate** — Run a full maintenance pipeline across repositories: pull → scan → fix → review → merge → sync → release, with human checkpoints and resume support
- **ghs-dev-loop** — Act as an autonomous developer for a repository: triage → analyze → implement → review → merge, with priority queue, issue budgets, and cycle modes

### Utilities

- **ghs-repos-pull** — Pull (update) all locally cloned repositories in repos/ to keep them fresh before scanning or fixing
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
