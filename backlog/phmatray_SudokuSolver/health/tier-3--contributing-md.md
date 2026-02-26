# CONTRIBUTING.md

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | PASS |
| **PR** | https://github.com/phmatray/SudokuSolver/pull/19 |
| **Detected** | 2026-02-26 |

## What's Missing

No CONTRIBUTING.md file exists in the repository.

## Why It Matters

Without contribution guidelines, potential contributors don't know how to set up the project, what coding standards to follow, or how to submit changes. This creates friction and may discourage contributions to the project.

## How to Fix

### Quick Fix

```bash
cat > CONTRIBUTING.md <<'EOF'
# Contributing to SudokuSolver

## Getting Started

1. Fork the repository
2. Clone your fork
3. Install .NET SDK 10.0+
4. Run `dotnet build` to verify setup

## Making Changes

1. Create a feature branch from `main`
2. Make your changes
3. Run `dotnet test` to verify
4. Submit a pull request

## Code Style

- Follow standard C# conventions
- Use meaningful variable and method names
EOF
```

### Full Solution

Include sections on: prerequisites, local setup, coding conventions, testing, and the PR review process.

## Acceptance Criteria

- [x] CONTRIBUTING.md file exists in the repository root

## References

- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
