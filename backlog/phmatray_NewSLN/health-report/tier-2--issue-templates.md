# Issue Templates

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No issue templates found in `.github/ISSUE_TEMPLATE/`.

## Why It Matters

Without issue templates, bug reports and feature requests lack consistent structure. This makes triage harder and means important details (reproduction steps, expected behavior) are often missing.

## How to Fix

### Quick Fix

```bash
mkdir -p .github/ISSUE_TEMPLATE && cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug Report
about: Report a bug to help us improve
labels: bug
---

## Description
A clear description of the bug.

## Steps to Reproduce
1. ...

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS:
- .NET version:
EOF
git add .github/ISSUE_TEMPLATE/ && git commit -m "Add issue templates" && git push
```

### Full Solution

Add both `bug_report.md` and `feature_request.md` templates, plus a `config.yml` to customize the issue chooser.

## Acceptance Criteria

- [ ] `.github/ISSUE_TEMPLATE/` directory exists with at least one template file

## References

- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
