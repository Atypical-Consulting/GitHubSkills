# Branch Protection

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 1 — Required |
| **Points** | 4 |
| **Status** | PASS |
| **Detected** | 2026-02-26 |

## What's Missing

The default branch `main` has no branch protection rules configured.

## Why It Matters

Without branch protection, anyone with write access can push directly to `main`, force-push over history, or merge without code review. This increases the risk of accidental breakage and makes it harder to enforce quality gates like CI checks passing before merge.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/SudokuSolver/branches/main/protection -X PUT --input - <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF
```

### Full Solution

Configure branch protection through GitHub Settings > Branches > Add rule for `main`:

1. **Require pull request reviews** — at least 1 approving review
2. **Require status checks to pass** — add your CI workflow once it exists
3. **Include administrators** — apply rules to repo admins too
4. **Restrict force pushes** — prevent history rewriting

Note: You must be a repository admin to configure branch protection.

## Acceptance Criteria

- [x] `gh api repos/phmatray/SudokuSolver/branches/main/protection` returns HTTP 200
- [x] Direct pushes to `main` are blocked

## References

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
