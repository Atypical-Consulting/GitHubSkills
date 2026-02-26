# PR Template

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No pull request template found in any standard location.

## Why It Matters

Without a PR template, contributors may submit PRs without describing their changes, linking issues, or confirming they've tested their work. This slows reviews and increases the chance of incomplete merges.

## How to Fix

### Quick Fix

```bash
mkdir -p .github && cat > .github/pull_request_template.md << 'EOF'
## Summary

Brief description of changes.

## Related Issue

Closes #

## Changes

-

## Checklist

- [ ] Tests pass locally
- [ ] Code follows project conventions
- [ ] Documentation updated (if applicable)
EOF
git add .github/pull_request_template.md && git commit -m "Add PR template" && git push
```

### Full Solution

Customize the template to match your team's workflow. Consider adding sections for screenshots, breaking changes, or migration steps.

## Acceptance Criteria

- [ ] PR template exists in any standard location (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, or `.github/PULL_REQUEST_TEMPLATE/`)

## References

- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
