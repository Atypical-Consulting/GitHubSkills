# PR Template

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No pull request template exists in any standard location.

## Why It Matters

A PR template guides contributors to provide context, link related issues, and follow a checklist before requesting review. This reduces back-and-forth and ensures consistent PR quality.

## How to Fix

### Quick Fix

```bash
cat > .github/pull_request_template.md << 'EOF'
## Summary

<!-- Brief description of the changes -->

## Related Issue

<!-- Link to the related issue, e.g., Fixes #123 -->

## Changes

-

## Checklist

- [ ] Tests pass locally (`dotnet test`)
- [ ] Code follows project conventions
- [ ] Documentation updated (if applicable)
EOF
```

### Full Solution

Create `.github/pull_request_template.md` with the template above. Customize the checklist items to match your CI pipeline (e.g., add code coverage thresholds, Docker build checks).

## Acceptance Criteria

- [ ] A PR template file exists at `.github/pull_request_template.md` or equivalent location

## References

- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
