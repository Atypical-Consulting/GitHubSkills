# Output Conventions Reference

Terminal output patterns used across all GitHubSkills skills. Consistent formatting makes reports scannable and familiar.

## Status Indicators

| Indicator | Meaning | Used In |
|-----------|---------|---------|
| `[PASS]` | Check passed / fix applied | repo-scan, backlog-fix |
| `[FAIL]` | Check failed / fix failed | repo-scan, backlog-fix |
| `[WARN]` | Cannot verify (permissions) | repo-scan |
| `[INFO]` | Informational only | repo-scan |
| `[NEEDS_HUMAN]` | Requires manual intervention | backlog-fix, issue-implement |
| `[FAILED]` | Agent/operation failed | backlog-fix, issue-implement |

## Health Check Report Structure

```
## Repository Scan: {owner}/{repo}

### Health Checks

#### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [FAIL] LICENSE — Not found
  [WARN] Branch protection — Unable to check (requires admin access)

#### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [FAIL] .editorconfig — Not found

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [INFO] FUNDING.yml — Not found (optional)

---

### Health Score: 14/51 (27%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  6/26  ██░░░░░░ (23%)
  Tier 3:  0/9   ░░░░░░░░ (0%)
```

## Progress Bar Format

```
Width:  8 characters
Filled: █  (U+2588)
Empty:  ░  (U+2591)
```

## Table Patterns

### Dashboard Table (multi-repo)

```
| Repository | Health | Progress | Issues | Open | PRs | Last Scan |
|------------|--------|----------|--------|------|-----|-----------|
| owner/repo | 10/31 (32%) | ██░░░░░░ | 18 | 15 | 3 | 2026-02-26 |
```

### Item List Table

```
| # | Item | Tier | Points | Status | Issue | PR |
|---|------|------|--------|--------|-------|----|
| 1 | README | 1 | 4 | FAIL | #42 | — |
```

### Results Table (post-fix)

```
| Item | Tier | Pts | Status | PR |
|------|------|-----|--------|----|
| LICENSE | T1 | 4 | [PASS] | #12 |
| Branch Protection | T1 | 4 | [PASS] | — (API) |
```

### Issue Table

```
| # | Title | Labels | Age | Assignee |
|---|-------|--------|-----|----------|
| 42 | Login page crashes | bug | 12d | @user |
```

### Batch Plan Table

```
| # | Item | Tier | Pts | Category | Issue | Branch | Worktree |
|---|------|------|-----|----------|-------|--------|----------|
| 1 | LICENSE | T1 | 4 | B (file) | #42 | fix/license | repos/.../ |
```

## Summary Block Patterns

Each skill ends with a `Summary:` block using indented key-value pairs:

- **backlog-fix**: Applied, PRs created, Points recovered, New health score
- **backlog-sync**: Created, Updated, Reopened, Closed, Already synced, Skipped
- **issue-triage**: Triaged count, Types breakdown, Priority breakdown
- **merge-prs**: Merged, Failed, Skipped counts

## Issue Display Limits

| Constant | Value |
|----------|-------|
| Max terminal issues | 20 (note "+N more" if exceeded) |
| Issue body truncation | 500 chars in backlog files |
| Title kebab truncation | 50 chars |
| Classification body limit | 2000 chars |

## Next Action Recommendation Block

```
### Recommended Next

The highest-impact item is **{name}** (Health — Tier {N}, {points} points).
To apply it:

  /ghs-backlog-fix {owner}/{repo} --item {slug}
```

## Routing Suggestions

Skills suggest next steps at the end of their output:

| After | Suggest |
|-------|---------|
| repo-scan | backlog-sync, backlog-fix, backlog-board |
| backlog-fix | merge-prs, backlog-board, repo-scan |
| backlog-sync | backlog-fix, backlog-board |
| backlog-board | backlog-fix, repo-scan, backlog-next |
| issue-triage | issue-analyze, issue-implement |
| issue-analyze | issue-implement |
| issue-implement | merge-prs |
| merge-prs | repo-scan, backlog-board |
