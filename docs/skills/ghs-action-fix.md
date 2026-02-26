# ghs-action-fix

Fix failing GitHub Actions pipelines directly — detect broken workflows, diagnose from run logs, apply fixes, and create PRs. No prior scan or backlog required.

::: info Skill Info
**Version:** 2.0.0
**Trigger phrases:** "fix my pipeline", "fix CI", "my actions are failing", "fix my workflows", "repair my build", "CI is broken", "fix GitHub Actions", "debug my workflow", "why is my build failing", "action fix"
:::

## What It Does

`ghs-action-fix` detects failing GitHub Actions workflows, reads their run logs, diagnoses root causes, and applies targeted fixes — each in its own worktree with a dedicated PR.

### How It Differs from ghs-backlog-fix

| Skill | When to Use |
|-------|-------------|
| `ghs-backlog-fix` | Fix pre-existing backlog items from a scan |
| `ghs-action-fix` | **Direct**: "my CI is broken" — detect, diagnose, fix, PR |

### Scope Boundary

**Only modifies** `.github/workflows/` files. If CI fails due to broken application code (test failures, compilation errors), the skill reports `NEEDS_HUMAN` with a diagnosis instead of attempting a fix.

### Process

1. **Detect** — Find failing workflows via `gh run list`
2. **Prepare** — Clone/pull repo, detect tech stack
3. **Confirm** — Show triage table, wait for user confirmation
4. **Worktrees** — One worktree per failing workflow (`fix/action-{slug}`)
5. **Agents** — Spawn parallel CI Fix Agents (one per workflow)
6. **Collect** — Parse results, apply circuit breaker (3 attempts max)
7. **Cleanup** — Remove worktrees for PASS/FAILED; preserve NEEDS_HUMAN
8. **Report** — Show results table with PR links and NEEDS_HUMAN instructions

### Root Cause Classification

Each CI Fix Agent classifies failures before acting:

| Category | Examples | Action |
|----------|----------|--------|
| WORKFLOW_FIX | Deprecated actions, wrong runtime versions, missing permissions, YAML errors | Fix the workflow file |
| APP_CODE | Test failures, compilation errors, missing imports | NEEDS_HUMAN |
| ENVIRONMENT | Expired secrets, missing repo variables | NEEDS_HUMAN |

## Example

```
## Failing Workflows: phmatray/my-project

| # | Workflow | File     | Last Run | Branch | Run ID |
|---|----------|----------|----------|--------|--------|
| 1 | CI       | ci.yml   | failure  | main   | 12345  |
| 2 | Deploy   | deploy.yml | failure | main   | 12346  |

Workflows to fix: 2

Proceed with all? (y/n)
```

After fixing:

```
## Results: phmatray/my-project

| Workflow | File       | Diagnosis             | Status        | PR  |
|----------|------------|-----------------------|---------------|-----|
| CI       | ci.yml     | Node 16 → 20 upgrade | [PASS]        | #42 |
| Deploy   | deploy.yml | Broken app test       | [NEEDS_HUMAN] | —   |

---

Summary:
  Fixed: 1/2
  PRs created: 1

Needs human attention:
  [NEEDS_HUMAN] Deploy (deploy.yml) — CI fails due to broken test in
    src/auth.test.ts, not a workflow issue
```

## Routes To

After fixing, GHS suggests:

- **[ghs-merge-prs](/skills/ghs-merge-prs)** — to merge the created PRs
- **[ghs-repo-scan](/skills/ghs-repo-scan)** — to run a full health check

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Task` |
| Spawns sub-agents | Yes — one CI Fix Agent per failing workflow, parallel execution |
| Phases | 8 (Detect, Prepare, Confirm, Worktrees, Agents, Collect, Cleanup, Report) |
| Circuit breaker | 3 attempts per workflow, then NEEDS_HUMAN |
| Requires | `gh` CLI (authenticated), `git`, network access, write access to repo |
| Re-run safe | Yes — only targets currently failing workflows |
