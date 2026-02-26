# PR Template

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | PASS |
| **PR** | https://github.com/phmatray/SudokuSolver/pull/17 |
| **Detected** | 2026-02-26 |

## What's Missing

No pull request template found in any standard location.

## Why It Matters

A PR template ensures that every pull request includes a summary of changes, related issues, and a testing checklist. This speeds up code review and reduces the chance of merging incomplete work.

## How to Fix

### Quick Fix

```bash
cat > .github/pull_request_template.md <<'EOF'
## Summary

## Related Issues

## Changes

-

## Checklist

- [ ] Code builds without errors
- [ ] Tests pass
- [ ] Self-reviewed
EOF
```

### Full Solution

Place the template at `.github/pull_request_template.md`. It will automatically populate the PR description for all new pull requests.

## Acceptance Criteria

- [x] PR template exists in any standard location (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, or `.github/PULL_REQUEST_TEMPLATE/`)

## References

- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
