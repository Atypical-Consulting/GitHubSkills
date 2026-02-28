---
name: ghs-repos-pull
description: >
  Pull (update) all locally cloned repositories in the repos/ directory.
  Trigger: "pull all repos", "update all repos", "git pull repos", "refresh repos", "sync repos"
argument-hint: "(no arguments)"
allowed-tools: "Bash(git:*) Bash(ls:*) Bash(find:*) Read Glob"
compatibility: "Requires git, network access"
license: MIT
metadata:
  author: phmatray
  version: 1.0.0
routes-from:
  - ghs-repo-scan
  - ghs-backlog-fix
---

<context>
<execution_context>
References:
- ../shared/references/gh-cli-patterns.md
- ../shared/references/output-conventions.md
- ../shared/references/ui-brand.md
- ../shared/references/argument-parsing.md
</execution_context>

<required_reading>
Verify `repos/` directory exists before iterating.
</required_reading>

## Purpose

Iterate over every cloned repository under `{repoRoot}/repos/` and run `git pull` on the default branch. This keeps local clones fresh before scanning, fixing, or any other operation that reads repo contents.

## Shared References

| Path | Use For |
|------|---------|
| `../shared/references/output-conventions.md` | Status indicators, progress display |
| `../shared/references/edge-cases.md` | Network errors, auth failures |

## Key Definitions

| Term | Meaning |
|------|---------|
| `{repoRoot}` | The project root where `repos/` lives (auto-detected from working directory) |
| Repo clone | A directory under `repos/` matching `{owner}_{repo}` (no `--worktrees` suffix) |
| Worktree dir | A directory under `repos/` matching `*--worktrees` — **skipped** by this skill |

</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Pull inside `--worktrees` directories | Skip anything matching `*--worktrees` | Worktrees have detached HEADs; pulling corrupts them |
| Pull on non-default branches | Checkout default branch first, then pull | Pulling on a feature branch may cause merge conflicts |
| Fail hard on a single repo error | Log `[FAIL]` and continue to next repo | One broken clone shouldn't block all updates |
| Run pulls sequentially with no progress | Show a counter `[3/14]` per repo | User needs feedback during long operations |
| Use `gh repo sync` | Use `git pull` | `gh repo sync` is for forks; `git pull` is simpler for local clones |

</anti-patterns>

<objective>

**Goal**: Update every cloned repository in `repos/` to the latest state of its default branch.

**Outputs**:
- Terminal summary table showing each repo's pull result (`[PASS]`, `[FAIL]`, `[SKIP]`)
- Count of updated / failed / skipped repos

**Next**: Any skill that reads from `repos/` (e.g., `ghs-repo-scan`, `ghs-backlog-fix`)

</objective>

<required_reading>
- Check repos/ directory exists before attempting to list or pull repositories
</required_reading>

<process>

## Phase 1 — Discover Repos

1. Resolve `{repoRoot}` — walk up from the current working directory until you find a directory containing `repos/`. Typically the GitHubSkills project root.
2. List all directories directly under `repos/`.
3. Filter:
   - **Include**: directories matching `{owner}_{repo}` (contain a `.git` directory or file).
   - **Exclude**: directories ending with `--worktrees`.
   - **Exclude**: any non-directory entries.
4. Sort alphabetically for predictable output order.
5. Store the list and total count `{N}`.

**Rule**: If no repos are found, print `[INFO] No cloned repositories found in repos/. Run ghs-repo-scan first.` and stop.

## Phase 2 — Pull Each Repo

For each repo directory `repos/{owner}_{repo}` (index `{i}` of `{N}`):

1. Print progress: `[{i}/{N}] {owner}/{repo} ...`
2. Detect the default branch:
   ```bash
   git -C repos/{owner}_{repo} symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'
   ```
   If that fails, fall back to `main`, then `master`.
3. Ensure we're on the default branch:
   ```bash
   git -C repos/{owner}_{repo} checkout {default_branch} --quiet 2>&1
   ```
4. Pull latest:
   ```bash
   git -C repos/{owner}_{repo} pull --ff-only --quiet 2>&1
   ```
5. Record result:
   - Exit 0 → `[PASS]`
   - Non-zero → `[FAIL]` with the error message (trimmed to one line)

**Rule**: Use `--ff-only` to avoid creating merge commits. If fast-forward fails, record `[FAIL]` with reason "diverged — needs manual resolution".

**Rule**: Timeout each pull at 60 seconds. If exceeded, record `[FAIL]` with reason "timeout".

## Phase 3 — Summary

Print a summary table:

```
## Repos Pull Summary

| # | Repository               | Status  | Detail           |
|---|--------------------------|---------|------------------|
| 1 | phmatray/Formidable      | [PASS]  | Already up to date |
| 2 | phmatray/NewSLN          | [PASS]  | 3 commits pulled |
| 3 | phmatray/BrokenRepo      | [FAIL]  | diverged          |

---
Total: 14 | Updated: 12 | Already current: 1 | Failed: 1
```

**Rule**: If all repos passed, end with `[PASS] All {N} repositories are up to date.`
**Rule**: If any failed, end with `[WARN] {F} of {N} repositories failed to update. Check the table above.`

</process>

<examples>

### Good Output

```
## Pulling 14 repositories...

[ 1/14] Atypical-Consulting/dotnet-clean-architecture ... [PASS] Already up to date
[ 2/14] Atypical-Consulting/VirtualFileSystem ........... [PASS] 2 commits pulled
[ 3/14] phmatray/Antlr4Library .......................... [PASS] Already up to date
...
[14/14] phmatray/TheAppManager .......................... [PASS] 1 commit pulled

---
Total: 14 | Updated: 8 | Already current: 6 | Failed: 0

[PASS] All 14 repositories are up to date.
```

### Bad Output

```
Pulling repos...
done
```

(No per-repo status, no counts, no progress — unacceptable.)

</examples>
