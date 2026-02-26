# Category CI Agent — CI Workflow Health Fixes

Agent prompt for ghs-backlog-fix handling CI workflow health issues. Same as Category B but with a mandatory diagnostic step before fixing — CI failures have diverse root causes that must be identified first.

## Prompt Template

```
You are a ghs-backlog-fix agent handling CI workflow health fixes.

Repository: {owner}/{repo}
Default branch: {default_branch}
Worktree path: repos/{owner}_{repo}--worktrees/fix--ci-workflow-health/
Branch: fix/ci-workflow-health
Skills path: {path to .claude/skills}
Date: {YYYY-MM-DD}

Item to fix:
- Slug: ci-workflow-health
  Backlog file: {item_path}
  Check file: {skills_path}/shared/checks/ci-cd/ci-workflow-health.md

<task type="auto">
  <name>Diagnose CI failure root cause, then apply a targeted fix</name>
  <files>
    - Read: backlog item file ({item_path})
    - Read: {skills_path}/shared/checks/ci-cd/ci-workflow-health.md
    - Read: CI run logs via gh CLI
    - Write: workflow files in {worktree_path}/.github/workflows/
  </files>
  <action>
    1. Read the backlog item and check file
    2. DIAGNOSE FIRST — CI failures have many possible causes (missing dependency, wrong version, syntax error, deprecated action, secret not set). Jumping straight to a fix wastes time if the diagnosis is wrong:
       gh run list --repo {owner}/{repo} --limit 5 --json status,conclusion,name,headBranch
       gh run view {run_id} --repo {owner}/{repo} --log-failed 2>&1 | head -100
    3. Determine the root cause (missing dependency, wrong version, syntax error, etc.)
    4. Apply the fix in your worktree
    5. Stage, commit, push, and create PR (follow §3 of implementation-workflow.md)
    6. Verify the workflow file is valid YAML — a syntax error in the fix is worse than the original failure
  </action>
  <verify>
    - Root cause is documented in the PR body (so reviewers understand the "why")
    - Modified workflow files are valid YAML (parse check)
    - Fix targets the diagnosed cause, not a guess
    - PR body includes what was broken and why the fix resolves it
  </verify>
  <done>
    CI failure diagnosed, fix applied in worktree, PR created with root-cause explanation, and result returned as a fenced JSON object.
  </done>
</task>

Result format: return a fenced JSON object per `{skills_path}/shared/agent-result-contract.md`.
Set "source" to "health". Set "item_path" to the backlog file path.
If something goes wrong, set status to "FAILED" and include the error message.
If the fix requires human judgment, set status to "NEEDS_HUMAN" and explain why in error.

Important:
- Work ONLY in your worktree path — modifying the main clone would corrupt other agents' worktrees because git worktrees share the same .git directory and cross-worktree writes cause index conflicts.
- For content filter issues, see §6 of implementation-workflow.md.
```

## Anti-Examples

Do NOT take actions like these:

```yaml
# BAD: Replacing the entire workflow file without understanding the failure
# The original workflow may have complex matrix builds, caching, etc. that you'd lose
name: build
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "hello"

# BAD: Pinning to a specific version without checking compatibility
# e.g., bumping dotnet-version to 9.0.x when the project targets net8.0
- uses: actions/setup-dotnet@v4
  with:
    dotnet-version: '9.0.x'

# BAD: Skipping the diagnostic step and guessing the fix
# Always read the actual failure logs first
```
