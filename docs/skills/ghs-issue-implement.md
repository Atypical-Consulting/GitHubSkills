# ghs-issue-implement

Implements GitHub issues using parallel worktree-based agents, then creates PRs with auto-close references.

::: info Skill Info
**Version:** 2.0.0
**Trigger phrases:** "implement issue #123", "fix issue #5", "build feature from issue #15", "implement all triaged issues", "implement all bugs", "code issue #42"
:::

## What It Does

`ghs-issue-implement` spawns parallel agents to implement GitHub issues. Each agent works in its own git worktree with a dedicated branch, writes code, runs tests, commits, pushes, and creates a PR that auto-closes the issue on merge.

### Branch Naming

Branches are named based on the issue's type label:

| Type Label | Branch Prefix | Example |
|-----------|---------------|---------|
| `type:bug` | `fix/` | `fix/42-login-crash` |
| `type:feature` | `feat/` | `feat/15-dark-mode` |
| `type:docs` | `docs/` | `docs/18-update-readme` |
| `type:hotfix` | `fix/` | `fix/99-security-vuln` |
| (default) | `impl/` | `impl/50-misc-task` |

### Analysis Context

If an issue has a prior analysis comment from `ghs-issue-analyze` (starting with `## Issue Analysis`), the implementation agent receives it as context. This provides affected files, suggested approach, and complexity assessment, saving significant investigation time.

### Process

1. Fetch issues from GitHub (single, by label, or by type)
2. Clone or pull the repository, detect tech stack
3. Show the implementation plan and wait for confirmation
4. Create worktrees for each issue
5. Launch all agents in parallel
6. Collect results, retry transient failures once
7. Update issue labels to `status:in-progress`
8. Clean up worktrees (except NEEDS_HUMAN items)
9. Display final results report

## Example

```
## Implementation Plan: phmatray/my-project

| # | Issue                | Type    | Priority | Branch              | Has Analysis? |
|---|----------------------|---------|----------|---------------------|---------------|
| 1 | #42 Login crashes    | bug     | high     | fix/42-login-crash  | Yes           |
| 2 | #15 Add dark mode    | feature | medium   | feat/15-dark-mode   | No            |
| 3 | #18 Update README    | docs    | low      | docs/18-update-readme| No           |

Total: 3 issues (1 bug, 1 feature, 1 docs)

Proceed with all? (y/n/select)
```

After completion:

```
## Results: phmatray/my-project

| # | Issue             | Type    | Status        | PR   |
|---|-------------------|---------|---------------|------|
| #42| Login crashes    | bug     | [PASS]        | #101 |
| #15| Add dark mode    | feature | [NEEDS_HUMAN] | --   |
| #18| Update README    | docs    | [PASS]        | #102 |

---

Summary:
  Implemented: 2/3
  PRs created: 2
  By type: 1 bug, 0 features, 1 docs

Remaining:
  [NEEDS_HUMAN] #15 Add dark mode — worktree at repos/phmatray_my-project--worktrees/feat--15-dark-mode/
    Reason: Feature requires design decisions about theme system architecture
```

## Routes To

After implementing, GHS suggests:

- **[ghs-merge-prs](/skills/ghs-merge-prs)** — to merge the created PRs

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Task` |
| Spawns sub-agents | Yes — one implementation agent per issue, all launched in parallel |
| Phases | 8 (Fetch Issues, Prepare Repo, Show Plan, Create Worktrees, Launch Agents, Collect Results, Cleanup, Report) |
| Requires | `gh` CLI (authenticated), `git`, network access, write access to repo |
| Re-run safe | Yes — skips issues already with `status:in-progress` and an open PR |
