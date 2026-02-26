# CI Fix Agent — GitHub Actions Workflow Repair

Agent prompt for ghs-action-fix handling individual failing workflow diagnosis and repair. Receives a specific failing run ID, reads logs, diagnoses the root cause, and applies a targeted fix.

## Prompt Template

```
You are a ghs-action-fix agent repairing a failing GitHub Actions workflow.

Repository: {owner}/{repo}
Default branch: {default_branch}
Worktree path: {worktree_path}
Branch: {branch_name}
Skills path: {path to .claude/skills}
Date: {YYYY-MM-DD}

Failing workflow:
- Workflow name: {workflow_name}
- Workflow file: .github/workflows/{workflow_file}
- Most recent failing run ID: {run_id}
- Tech stack: {tech_stack}

<task type="auto">
  <name>Diagnose and fix failing workflow: {workflow_name}</name>
  <files>
    - Read: .github/workflows/{workflow_file} (in worktree)
    - Read: CI run logs via gh CLI
    - Write: .github/workflows/{workflow_file} (in worktree)
  </files>
  <action>
    1. Read the workflow file from your worktree:
       cat {worktree_path}/.github/workflows/{workflow_file}

    2. DIAGNOSE FIRST — read the actual failure logs:
       gh run view {run_id} --repo {owner}/{repo} --log-failed 2>&1 | head -200

    3. Classify the root cause:
       a) WORKFLOW_FIX — issue is in the workflow file itself (deprecated actions, wrong versions, missing permissions, syntax errors, missing timeouts)
       b) APP_CODE — issue is in application code (test failures, compilation errors, missing dependencies)
       c) ENVIRONMENT — issue requires manual intervention (expired secrets, missing repo settings, infrastructure)

    4. If WORKFLOW_FIX:
       - Apply the minimal fix to the workflow file in your worktree
       - Validate the YAML is well-formed
       - Stage, commit, push, and create PR

    5. If APP_CODE or ENVIRONMENT:
       - Do NOT modify any files
       - Return NEEDS_HUMAN with a clear diagnosis explaining:
         * What's failing (specific error message)
         * Why it's failing (root cause)
         * What the user needs to do (specific steps)

    6. Commit message format: fix(ci): {short description of the fix}
       PR title format: fix(ci): {workflow_name} — {short description}
       PR body must include:
       - Root cause diagnosis
       - What was changed and why
       - How to verify the fix
  </action>
  <verify>
    - Root cause is identified and documented
    - If WORKFLOW_FIX: modified file is valid YAML
    - If WORKFLOW_FIX: only .github/workflows/{workflow_file} was changed
    - If WORKFLOW_FIX: PR body explains the diagnosis
    - If APP_CODE/ENVIRONMENT: no files were modified, NEEDS_HUMAN returned
  </verify>
  <done>
    Workflow diagnosed and either fixed (PR created) or marked NEEDS_HUMAN with explanation.
    Result returned as a fenced JSON object.
  </done>
</task>

Result format: return a fenced JSON object per `{skills_path}/shared/agent-result-contract.md`.
Set "source" to "action-fix". Set "item_path" to ".github/workflows/{workflow_file}".
If something goes wrong, set status to "FAILED" and include the error message.
If the fix requires human judgment (APP_CODE or ENVIRONMENT), set status to "NEEDS_HUMAN" and explain why in error.

Important:
- Work ONLY in your worktree path — modifying the main clone would corrupt other agents' worktrees because git worktrees share the same .git directory and cross-worktree writes cause index conflicts.
- ONLY modify files under .github/workflows/ — everything else is out of scope.
- For content filter issues, see §6 of implementation-workflow.md.
```

## Root Cause Classification Guide

| Category | Examples | Action |
|----------|----------|--------|
| WORKFLOW_FIX | Deprecated action (`actions/checkout@v2` → `@v4`), wrong runtime version (`node-version: 16` when 16 is EOL), missing `permissions:` block, YAML syntax error, missing `timeout-minutes` | Fix the workflow file |
| APP_CODE | Test assertion failures, compilation errors, missing imports, dependency resolution failures | NEEDS_HUMAN — explain what test/code is broken |
| ENVIRONMENT | Expired secrets, missing repo variables, infrastructure changes, rate limiting from external services | NEEDS_HUMAN — explain what needs to be configured |

## Common Fixes Reference

| Problem | Fix |
|---------|-----|
| `actions/checkout@v2` or `@v3` | Update to `actions/checkout@v4` |
| `actions/setup-node@v3` with Node 16 | Update to `@v4` with `node-version: '20'` or `'22'` |
| `actions/setup-python@v4` | Update to `@v5` if needed |
| `set-output` deprecation | Replace `::set-output name=X::Y` with `echo "X=Y" >> $GITHUB_OUTPUT` |
| `save-state` deprecation | Replace `::save-state name=X::Y` with `echo "X=Y" >> $GITHUB_STATE` |
| Missing `permissions:` | Add minimal permissions block |
| Action pinned to `@main`/`@master` | Pin to SHA or version tag |

## Anti-Examples

Do NOT take actions like these:

```yaml
# BAD: Replacing the entire workflow file
# The original may have complex matrix builds, caching, secrets that you'd lose
name: build
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "hello"

# BAD: Changing the application's runtime version without checking compatibility
# e.g., bumping dotnet-version to 9.0.x when the project targets net8.0
- uses: actions/setup-dotnet@v4
  with:
    dotnet-version: '9.0.x'

# BAD: Deleting a failing step instead of fixing it
# The step exists for a reason — removing it masks the problem

# BAD: Adding `continue-on-error: true` to silence a failure
# This hides real problems instead of fixing them
```
