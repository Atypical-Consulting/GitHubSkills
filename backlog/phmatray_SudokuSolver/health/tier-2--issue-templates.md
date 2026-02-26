# Issue Templates

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | PASS |
| **PR** | https://github.com/phmatray/SudokuSolver/pull/16 |
| **Detected** | 2026-02-26 |

## What's Missing

No issue templates found in `.github/ISSUE_TEMPLATE/`.

## Why It Matters

Without issue templates, bug reports and feature requests lack structure. Contributors may omit key information (steps to reproduce, expected behavior), leading to back-and-forth clarification. Templates guide reporters to provide actionable details upfront.

## How to Fix

### Quick Fix

```bash
mkdir -p .github/ISSUE_TEMPLATE && cat > .github/ISSUE_TEMPLATE/bug_report.md <<'EOF'
---
name: Bug Report
about: Report a bug in SudokuSolver
labels: bug
---

## Description

## Steps to Reproduce

1.

## Expected Behavior

## Actual Behavior

## Environment
- OS:
- .NET version:
EOF
```

### Full Solution

Create at least two templates:
1. `bug_report.md` — for defects with reproduction steps
2. `feature_request.md` — for enhancements with use case context

## Acceptance Criteria

- [x] `.github/ISSUE_TEMPLATE/` directory exists with at least one file

## References

- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
