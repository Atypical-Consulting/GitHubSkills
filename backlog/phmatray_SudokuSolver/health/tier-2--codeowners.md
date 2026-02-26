# CODEOWNERS

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | PASS |
| **PR** | https://github.com/phmatray/SudokuSolver/pull/15 |
| **Detected** | 2026-02-26 |

## What's Missing

No CODEOWNERS file found in any standard location (root, `.github/`, or `docs/`).

## Why It Matters

Without a CODEOWNERS file, pull requests won't automatically request reviews from the right people. As the sole maintainer, this ensures you're always notified of PRs and sets a good pattern if contributors join later.

## How to Fix

### Quick Fix

```bash
mkdir -p .github && echo "* @phmatray" > .github/CODEOWNERS
```

### Full Solution

Create `.github/CODEOWNERS` with ownership rules:

```
# Default owner for everything
* @phmatray
```

## Acceptance Criteria

- [x] CODEOWNERS file exists in root, `.github/`, or `docs/`

## References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
