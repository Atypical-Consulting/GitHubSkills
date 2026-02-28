# ghs-repos-pull

Pull (update) all locally cloned repositories in the repos/ directory.

::: info Skill Info
**Version:** 1.0.0
**Arguments:** `(no arguments)`
**Trigger phrases:** "pull all repos", "update all repos", "git pull repos", "refresh repos", "sync repos"
:::

## What It Does

`ghs-repos-pull` iterates over every cloned repository under `repos/` and runs `git pull` on the default branch. This keeps local clones fresh before scanning, fixing, or any other operation that reads repo contents.

### Scope Boundary

**Read + pull only** --- checks out the default branch and pulls latest changes. Never creates branches, commits, or pushes.

### Process

1. **Discover repos** --- List directories under `repos/`, include those with `.git`, exclude `*--worktrees` directories
2. **Pull each repo** --- For each directory:
   - Detect the default branch
   - Checkout default branch
   - `git pull --ff-only`
   - Record result: `[PASS]`, `[FAIL]`, or `[SKIP]`
3. **Summary** --- Display a table with per-repo results and totals

### Key Rules

- **Skip worktrees** --- Directories ending with `--worktrees` have detached HEADs; pulling corrupts them
- **Fast-forward only** --- Uses `--ff-only` to avoid creating merge commits
- **Fail gracefully** --- One broken clone doesn't block all updates
- **Show progress** --- Counter `[3/14]` per repo for long operations
- **60-second timeout** --- Per-repo pull timeout to prevent hangs

## Example

```
## Pulling 14 repositories...

[ 1/14] Atypical-Consulting/dotnet-clean-architecture ... [PASS] Already up to date
[ 2/14] Atypical-Consulting/VirtualFileSystem ........... [PASS] 2 commits pulled
[ 3/14] phmatray/Antlr4Library .......................... [PASS] Already up to date
[ 4/14] phmatray/BrokenRepo ............................. [FAIL] diverged
...
[14/14] phmatray/TheAppManager .......................... [PASS] 1 commit pulled

---
Total: 14 | Updated: 8 | Already current: 5 | Failed: 1

[WARN] 1 of 14 repositories failed to update. Check the table above.
```

## Routes From

- **[ghs-repo-scan](/skills/ghs-repo-scan)** --- pull before scanning
- **[ghs-backlog-fix](/skills/ghs-backlog-fix)** --- pull before fixing

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(git:*)`, `Bash(ls:*)`, `Bash(find:*)`, `Read`, `Glob` |
| Spawns sub-agents | No |
| Phases | 3 (Discover, Pull, Summary) |
| Requires | `git`, network access |
