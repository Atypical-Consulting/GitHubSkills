# CODEOWNERS

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | PASS |
| **Detected** | 2026-02-26 |

## What's Missing

No CODEOWNERS file found in any standard location (root, `.github/`, or `docs/`).

## Why It Matters

Without CODEOWNERS, pull requests won't automatically request reviews from the right people. This slows down the review process and risks changes being merged without input from domain experts.

## How to Fix

### Quick Fix

```bash
mkdir -p .github && echo "* @phmatray" > .github/CODEOWNERS && git add .github/CODEOWNERS && git commit -m "Add CODEOWNERS" && git push
```

### Full Solution

Define ownership per directory or file pattern as the team grows:

```
# Default owner
* @phmatray

# Example: specific paths
# /src/api/ @backend-team
# /src/ui/  @frontend-team
```

## Acceptance Criteria

- [x] CODEOWNERS file exists in root, `.github/`, or `docs/`

## References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
