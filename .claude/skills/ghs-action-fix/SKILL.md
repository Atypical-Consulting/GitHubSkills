---
name: ghs-action-fix
description: >
  Fix failing GitHub Actions pipelines directly — detects broken workflows, reads run logs, diagnoses
  root causes, applies fixes in worktrees, and creates PRs. No prior repo scan or backlog required.
  Use this skill whenever the user wants to fix CI, repair a pipeline, debug Actions failures, or says
  things like "fix my pipeline", "fix CI", "my actions are failing", "fix my workflows", "repair my
  build", "CI is broken", "fix GitHub Actions", "debug my workflow", "why is my build failing", or
  "action fix". Do NOT use for scanning repos (use ghs-repo-scan), applying backlog items
  (use ghs-backlog-fix), or merging PRs (use ghs-merge-prs).
allowed-tools: "Bash(gh:*) Bash(git:*) Bash(python3:*) Read Write Edit Glob Grep Task"
compatibility: "Requires gh CLI (authenticated), git, network access"
license: MIT
metadata:
  author: phmatray
  version: 1.0.0
routes-to:
  - ghs-merge-prs
  - ghs-repo-scan
routes-from:
  - ghs-repo-scan
  - ghs-backlog-board
---

# Fix GitHub Actions Pipelines

Detect failing GitHub Actions workflows, diagnose root causes from run logs, apply targeted fixes in worktrees, and create PRs — all in one pass with no prior scan required.

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Do Instead |
|-------------|--------------|------------|
| Guessing the fix without reading logs | Wastes time, often makes things worse | Always run `gh run view --log-failed` first |
| Replacing entire workflow files | Loses complex matrix builds, caching, secrets | Make minimal, targeted changes |
| Fixing application code bugs | Out of scope — workflow skill, not app debugger | Report as NEEDS_HUMAN with diagnosis |
| Retrying the same fix > 3 times | Infinite loop risk | Circuit breaker: 3 attempts max, then NEEDS_HUMAN |
| Modifying files outside `.github/workflows/` | Scope violation — could break the app | Only touch workflow files |
| Skipping YAML validation after edits | Syntax errors are worse than the original failure | Always validate YAML before committing |

## Scope Boundary

**Modifies**: `.github/workflows/*.yml` and `.github/workflows/*.yaml` files only.

**Does NOT modify**: Application code, test files, configuration files, dependencies. If CI fails due to broken application code (test failures, compilation errors, missing dependencies), the skill reports NEEDS_HUMAN with a diagnosis of the root cause.

## Context Budget

What to pass to each CI Fix Agent:

| Pass | Do NOT Pass |
|------|-------------|
| Failing workflow file content | All workflow files |
| Failed run ID and log excerpt (first 200 lines) | Full run logs (too large) |
| Repository tech stack summary | Full repo file tree |
| Worktree path and branch name | Other agents' results |
| Workflow file path | Backlog items or scan results |

See `../shared/references/agent-spawning.md` for the full agent spawning protocol.

## Circuit Breaker

| Attempt | Action |
|---------|--------|
| 1st failure | Re-run agent with error context appended to prompt |
| 2nd failure | Re-run with error + stricter constraints |
| 3rd failure | Mark as `NEEDS_HUMAN`, preserve worktree, stop retrying |

After 3 failures on the same workflow, the orchestrator moves on. The worktree is left in place for manual continuation.

<context>
Purpose: Direct-action skill for fixing failing GitHub Actions pipelines — no backlog or prior scan needed.

Roles:
1. **Orchestrator** (you) — detects failures, prepares repo, creates worktrees, spawns agents, collects results, cleans up
2. **CI Fix Agents** — one per failing workflow, each diagnosing and fixing in its own worktree

Agent prompt: `agents/ci-fix-agent.md`

Shared docs:
- `../shared/references/agent-spawning.md` — worktree creation, agent spawning, context budgeting
- `../shared/references/gh-cli-patterns.md` — authentication, repo detection, error handling
- `../shared/references/output-conventions.md` — status indicators, table formats, summary blocks
- `../shared/implementation-workflow.md` — §1 Repo Prep, §2 Worktree Mgmt, §3 Branch/Commit/Push/PR

The user must have **write access** to the target repository.
</context>

<objective>
Detect, diagnose, and fix failing GitHub Actions workflows, then create PRs.

Outputs:
- PRs created on GitHub for each fixed workflow
- Terminal report with diagnosis summaries and PR links
- NEEDS_HUMAN items listed with root-cause explanations

Next routing:
- Suggest `ghs-merge-prs` to merge the created PRs — "To merge: `/ghs-merge-prs {owner}/{repo}`"
- Suggest `ghs-repo-scan` to run a full health check
</objective>

<process>

## Input

- **Explicit repo**: `ghs-action-fix owner/repo`
- **Implicit repo**: `ghs-action-fix` (detects from `gh repo view`)
- **Specific workflow**: `ghs-action-fix owner/repo --workflow ci.yml`

## Phase 1 — Detect Failing Workflows

```bash
gh run list --repo {owner}/{repo} --limit 30 --json conclusion,workflowName,status,databaseId,headBranch,event 2>&1
```

Group runs by workflow name. For each workflow, find the most recent completed run. Identify workflows where the most recent completed run has `conclusion: "failure"`.

If no failing workflows found:
```
All GitHub Actions workflows are passing. Nothing to fix.
```

## Phase 2 — Prepare Repository

Follow `../shared/implementation-workflow.md` §1:
1. Clone or pull the repo into `repos/{owner}_{repo}/`
2. Detect the default branch: `gh repo view {owner}/{repo} --json defaultBranchRef --jq '.defaultBranchRef.name'`
3. Detect tech stack (language, framework, package manager) from repo contents

See `../shared/references/agent-spawning.md` (Repository Cloning section).

## Phase 3 — Confirm with User

Show a triage table of failing workflows:

```
## Failing Workflows: {owner}/{repo}

| # | Workflow | File | Last Run | Branch | Event | Run ID |
|---|----------|------|----------|--------|-------|--------|
| 1 | CI | ci.yml | failure | main | push | 12345 |
| 2 | Deploy | deploy.yml | failure | main | push | 12346 |

Workflows to fix: {N}
Branches to create: fix/action-{slug} per workflow

Proceed with all? (y/n/select)
```

Wait for user confirmation.

## Phase 4 — Create Worktrees

For each confirmed workflow:

| Step | Command | Notes |
|------|---------|-------|
| 1. Create worktree dir | `mkdir -p repos/{owner}_{repo}--worktrees` | Sibling to main clone |
| 2. Derive slug | Workflow filename without extension, kebab-case | `ci.yml` → `ci`, `code-quality.yml` → `code-quality` |
| 3. Add worktree | `git -C repos/{owner}_{repo} worktree add ../repos/{owner}_{repo}--worktrees/fix--action-{slug} -b fix/action-{slug}` | One per workflow |
| 4. Verify | `ls repos/{owner}_{repo}--worktrees/fix--action-{slug}/.git` | Confirm valid |

## Phase 5 — Launch CI Fix Agents

Spawn all agents in a **single Task tool message** for parallel execution.

For each failing workflow, read `agents/ci-fix-agent.md` and substitute:
- `{owner}/{repo}` — repository identifier
- `{default_branch}` — default branch name
- `{worktree_path}` — path to the worktree
- `{branch_name}` — `fix/action-{slug}`
- `{workflow_file}` — workflow filename (e.g., `ci.yml`)
- `{run_id}` — most recent failing run ID
- `{workflow_name}` — human-readable workflow name
- `{tech_stack}` — detected tech stack summary

All agents use `subagent_type: general-purpose`.

## Phase 6 — Collect Results

After all agents complete:

1. Parse each agent's result (JSON per `../shared/agent-result-contract.md`)
2. Apply circuit breaker: if an agent returns FAILED, retry up to 2 more times (3 total)
3. After 3 failures, mark as NEEDS_HUMAN

## Phase 7 — Cleanup Worktrees

- **PASS**: Remove worktree (`git worktree remove`) and delete local branch
- **FAILED**: Remove worktree and local branch (fix didn't work anyway)
- **NEEDS_HUMAN**: Leave worktree in place with instructions

Prune: `git -C repos/{owner}_{repo} worktree prune`

## Phase 8 — Final Report

```
## Results: {owner}/{repo}

| Workflow | File | Diagnosis | Status | PR |
|----------|------|-----------|--------|----|
| CI | ci.yml | Node 16 → 20 upgrade | [PASS] | #42 |
| Deploy | deploy.yml | Broken app test | [NEEDS_HUMAN] | — |

---

Summary:
  Fixed: {n_pass}/{n_total}
  PRs created: {n_prs}

{If any NEEDS_HUMAN items:}
Needs human attention:
  [NEEDS_HUMAN] Deploy (deploy.yml) — CI fails due to broken test in src/auth.test.ts, not a workflow issue
    Worktree: repos/{owner}_{repo}--worktrees/fix--action-deploy/

Next steps:
  To merge PRs: /ghs-merge-prs {owner}/{repo}
  To scan full health: /ghs-repo-scan {owner}/{repo}
```

</process>

## Edge Cases

- **No failing workflows**: Report all green and exit.
- **Only application code failures**: Report NEEDS_HUMAN with root-cause diagnosis for each. Don't modify workflow files if the issue is in app code.
- **Workflow syntax errors**: Fix the YAML syntax. Validate with a YAML parser before committing.
- **Deprecated actions**: Update to latest versions (e.g., `actions/checkout@v2` → `@v4`).
- **Missing secrets**: Report NEEDS_HUMAN — secrets can only be set by the repo admin.
- **Rate limiting**: Back off and retry per `../shared/edge-cases.md`.
- **Workflow triggered by schedule/cron**: Include in detection but note that the fix can't be verified by a PR push.
- **Multiple failures in same workflow**: Agent addresses all failures in one fix.
- **Branch already exists**: Check with `git branch -l fix/action-{slug}`. If exists, use `-B` flag or ask user.

## Examples

**Example 1: Single failing workflow**
User says: "fix my CI"
Result: Detects 1 failing workflow (CI, ci.yml), shows triage table, user confirms, creates worktree, agent reads logs (Node 16 EOL), updates `node-version` to 20, creates PR.

**Example 2: Multiple failures**
User says: "fix actions for phmatray/Formidable"
Result: Detects 3 failing workflows, shows triage table, user selects 2, creates 2 worktrees, spawns 2 parallel agents, one fixes deprecated checkout action, other reports NEEDS_HUMAN (broken test), shows results.

**Example 3: All green**
User says: "fix my pipeline"
Result: Checks `gh run list`, all workflows passing. Reports "All GitHub Actions workflows are passing. Nothing to fix."

## Troubleshooting

**"No failing workflows found" but CI badge shows red**
The failing run may be on a non-default branch. Try: `gh run list --repo {owner}/{repo} --branch main --limit 5`

**"Permission denied" when pushing branch**
You need write access. Check: `gh repo view --json viewerPermission`

**Agent can't determine root cause**
If logs are truncated or unclear, the agent marks NEEDS_HUMAN. Check the full logs manually: `gh run view {run_id} --log`

**Worktrees not cleaned up**
Run `git -C repos/{owner}_{repo} worktree list` and remove stale ones: `git worktree remove <path>`
