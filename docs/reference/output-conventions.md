# Output Conventions

Terminal output patterns used across all GHS skills. Consistent formatting makes reports scannable and familiar.

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| `[PASS]` | Check passed / fix applied |
| `[FAIL]` | Check failed / fix failed |
| `[WARN]` | Cannot verify (permissions) |
| `[INFO]` | Informational only |
| `[NEEDS_HUMAN]` | Requires manual intervention |
| `[FAILED]` | Agent/operation failed |

## Health Check Report Structure

```
## Repository Scan: {owner}/{repo}

### Health Checks

#### Tier 1 --- Required
  [PASS] README.md --- Found (2.3 KB)
  [FAIL] LICENSE --- Not found
  [WARN] Branch protection --- Unable to check (requires admin access)

#### Tier 2 --- Recommended
  [PASS] .gitignore --- Found
  [FAIL] .editorconfig --- Not found

### Health Score: 14/51 (27%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  6/26  ██░░░░░░ (23%)
  Tier 3:  0/9   ░░░░░░░░ (0%)
```

## Progress Bar

```
Width:  8 characters
Filled: █  (U+2588)
Empty:  ░  (U+2591)
```

Filled count = `round(percentage / 100 x 8)`.

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
| 1 | README | 1 | 4 | FAIL | #42 | --- |
```

### Results Table (post-fix)

```
| Item | Tier | Pts | Status | PR |
|------|------|-----|--------|----|
| LICENSE | T1 | 4 | [PASS] | #12 |
| Branch Protection | T1 | 4 | [PASS] | --- (API) |
```

### Batch Plan Table

```
| # | Item | Tier | Pts | Category | Issue | Branch | Worktree |
|---|------|------|-----|----------|-------|--------|----------|
| 1 | LICENSE | T1 | 4 | B (file) | #42 | fix/license | repos/.../ |
```

## Summary Blocks

Each skill ends with a `Summary:` block. Key metrics per skill:

| Skill | Summary Fields |
|-------|---------------|
| backlog-fix | Applied, PRs created, Points recovered, New health score |
| backlog-sync | Created, Updated, Reopened, Closed, Already synced, Skipped |
| issue-triage | Triaged count, Types breakdown, Priority breakdown |
| merge-prs | Merged, Failed, Skipped |

## Display Limits

| Constant | Value |
|----------|-------|
| Max terminal issues | 20 (note "+N more" if exceeded) |
| Issue body truncation | 500 chars |
| Title kebab truncation | 50 chars |

## Routing Suggestions

Skills suggest next steps at the end of their output:

| After | Suggest |
|-------|---------|
| repo-scan | backlog-sync, backlog-fix, backlog-board |
| backlog-fix | merge-prs, backlog-board, repo-scan |
| backlog-sync | backlog-fix, backlog-board |
| issue-triage | issue-analyze, issue-implement |
| issue-analyze | issue-implement |
| issue-implement | merge-prs |
| merge-prs | repo-scan, backlog-board |
