# CODEOWNERS

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No CODEOWNERS file exists in any standard location (root, `.github/`, or `docs/`).

## Why It Matters

A CODEOWNERS file automatically assigns reviewers to pull requests based on file paths. This ensures the right people review changes and nothing slips through without oversight, especially important as the project grows.

## How to Fix

### Quick Fix

```bash
mkdir -p .github && echo "* @phmatray" > .github/CODEOWNERS
```

### Full Solution

Create `.github/CODEOWNERS` with path-based ownership:

```
# Default owner for everything
* @phmatray

# API-specific changes
/BelgiumVatChecker.Api/ @phmatray
/BelgiumVatChecker.Core/ @phmatray
/BelgiumVatChecker.Tests/ @phmatray
```

## Acceptance Criteria

- [ ] CODEOWNERS file exists in `.github/CODEOWNERS`, root, or `docs/`

## References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
