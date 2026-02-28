# ghs-repo-scan

Scans a GitHub repository against 38 health checks and fetches open issues, producing a scored report and structured GitHub Project items.

::: info Skill Info
**Version:** 6.0.0
**Arguments:** `[owner/repo]`
**Trigger phrases:** "scan my repo", "audit phmatray/my-project", "run a health check", "is my repo set up properly?", "what's missing from my project", "repo audit", "repository checklist"
:::

## What It Does

`ghs-repo-scan` is the entry point to the GHS health loop. It performs a comprehensive audit of your repository by spawning **4 parallel agents**:

1. **Tier 1 Agent** — checks the 4 required items (README, LICENSE, description, branch protection)
2. **Tier 2 Agent** — checks the 20 recommended items (CI/CD, .editorconfig, templates, etc.)
3. **Tier 3 Agent** — checks the 14 nice-to-have items (SECURITY.md, CONTRIBUTING.md, etc.)
4. **Issues Agent** — fetches all open GitHub issues and creates them as GitHub Project items

After all agents complete, the orchestrator collects results, calculates the health score, creates a `[GHS Score]` project item in the GitHub Project, and displays a terminal report.

### Outputs

- `[GHS Score]` project item — unified repo summary with score breakdown, stored as a GitHub Project item
- One GitHub Project item per failing or warning health check
- One GitHub Project item per open issue
- Terminal report with health score, check results, and issue table

## Example

```
## Repository Scan: phmatray/my-project

### Health Checks

#### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [FAIL] LICENSE — Not found
  [PASS] Description — "A tool for automating GitHub workflows"
  [WARN] Branch protection — Unable to check (requires admin access)

#### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [PASS] CI/CD workflows — 3 workflow files found
  [FAIL] CI Workflow Health — 1 workflow failing (build.yml)
  [FAIL] .editorconfig — Not found
  ...

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [FAIL] CONTRIBUTING.md — Not found
  [INFO] FUNDING.yml — Not found (optional)
  ...

---

### Health Score: 14/51 (27%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  6/26  ██░░░░░░ (23%)
  Tier 3:  0/9   ░░░░░░░░ (0%)

---

### Open Issues — 18 total

| # | Title              | Labels      | Age  | Assignee |
|---|--------------------|-------------|------|----------|
| 42| Login page crashes  | bug         | 12d  | @user    |
| 108| Add dark mode      | enhancement | 45d  | --       |
...

Saved to GitHub Project: phmatray/my-project
  health/   — 8 items (8 FAIL, 0 WARN)
  issues/   — 18 items
```

## Routes To

After scanning, GHS suggests:

- **[ghs-backlog-fix](/skills/ghs-backlog-fix)** — to fix failing health checks
- **[ghs-backlog-board](/skills/ghs-backlog-board)** — to see the full dashboard
- **[ghs-issue-triage](/skills/ghs-issue-triage)** — to classify unlabeled issues (if all checks pass)

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Read`, `Glob`, `Task` |
| Spawns sub-agents | Yes — 4 parallel agents (3 health tier agents + 1 issues agent) |
| Phases | 5 (Setup, Spawn Agents, Collect Results, Update Project, Display Report) |
| Requires | `gh` CLI (authenticated), `git`, network access |
| Re-run safe | Yes — asks before overwriting health items, always syncs issues |
