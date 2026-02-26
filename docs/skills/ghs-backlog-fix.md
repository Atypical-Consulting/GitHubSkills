# ghs-backlog-fix

Applies backlog item fixes using parallel worktree-based agents -- clones the repo once, creates worktrees for each fix, launches agents simultaneously, verifies acceptance criteria, and creates PRs.

::: info Skill Info
**Version:** 7.0.0
**Trigger phrases:** "fix the backlog", "fix phmatray/my-project", "fix the failing checks", "apply this backlog item", "resolve all tier 1 items", "apply all for {repo}"
:::

## What It Does

`ghs-backlog-fix` is the most complex skill in GHS. It reads structured backlog items, classifies each into a category, and spawns parallel agents to fix them.

### Item Categories

| Category | Description | Worktree? | Example |
|----------|-------------|-----------|---------|
| **A** | API-only fixes (no file changes) | No | Setting repo description, enabling settings |
| **B** | File changes (each gets a worktree) | Yes | Adding LICENSE, creating .editorconfig |
| **CI** | CI diagnosis and fix | Yes | Fixing failing CI workflows |

### Two Modes

- **Single item** — provide a path to one backlog item file; GHS shows a focused plan and fixes just that item
- **Batch** — provide a repo identifier; GHS discovers all FAIL items, shows a batch plan table, and fixes them all in parallel after confirmation

### Process

1. Discover and classify all FAIL items
2. Clone or pull the repository
3. Show the batch plan and wait for user confirmation
4. Create worktrees for Category B and CI items
5. Launch all agents in parallel (one Task tool call)
6. Collect results, retry transient failures once
7. Update backlog items and SUMMARY.md with new scores
8. Clean up worktrees (except NEEDS_HUMAN items)
9. Display final results report

## Example

```
## Batch Plan: phmatray/my-project

| # | Item              | Tier | Pts | Category  | Branch           |
|---|-------------------|------|-----|-----------|------------------|
| 1 | LICENSE           | T1   | 4   | B (file)  | fix/license      |
| 2 | Branch Protection | T1   | 4   | A (API)   | --               |
| 3 | .editorconfig     | T2   | 2   | B (file)  | fix/editorconfig |
| 4 | CI Workflow Health | T2   | 2   | CI        | fix/ci-health    |

Total items: 4 (1 API-only, 2 file changes, 1 CI)
Points recoverable: 12

Proceed with all? (y/n/select)
```

After completion:

```
## Results: phmatray/my-project

| Item              | Tier | Pts | Status   | PR  |
|-------------------|------|-----|----------|-----|
| LICENSE           | T1   | 4   | [PASS]   | #12 |
| Branch Protection | T1   | 4   | [PASS]   | -- (API) |
| .editorconfig     | T2   | 2   | [PASS]   | #13 |
| CI Workflow Health | T2   | 2   | [FAILED] | --  |

---

Summary:
  Applied: 3/4
  PRs created: 2
  Points recovered: 10/12
  New health score: 73% (was 45%)

Remaining items:
  [FAILED] CI Workflow Health — build.yml requires manual investigation
```

## Routes To

After fixing, GHS suggests:

- **[ghs-merge-prs](/skills/ghs-merge-prs)** — to merge the created PRs
- **[ghs-backlog-board](/skills/ghs-backlog-board)** — to see the updated dashboard
- **[ghs-repo-scan](/skills/ghs-repo-scan)** — to re-scan and verify all fixes

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Bash(python3:*)`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Task` |
| Spawns sub-agents | Yes — Category A agent, Category B agents (one per item), Category CI agent |
| Phases | 8 (Discover, Prepare Repo, Show Plan, Create Worktrees, Launch Agents, Collect Results, Cleanup, Report) |
| Requires | `gh` CLI (authenticated), `git`, `python3`, network access, write access to repo |
| Re-run safe | Yes — skips already-PASS items, idempotent |
