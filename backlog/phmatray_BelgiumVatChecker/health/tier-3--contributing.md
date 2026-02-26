# CONTRIBUTING.md

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No CONTRIBUTING.md file exists in the repository.

## Why It Matters

A contributing guide lowers the barrier for new contributors by explaining how to set up the project, follow code conventions, and submit changes. For a .NET Web API project, this includes build prerequisites and testing instructions.

## How to Fix

### Quick Fix

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to BelgiumVatChecker

## Prerequisites

- .NET 10 SDK
- Docker (optional, for containerized development)

## Getting Started

1. Fork and clone the repository
2. Run `dotnet restore`
3. Run `dotnet build`
4. Run `dotnet test`

## Pull Requests

- Create a feature branch from `main`
- Follow existing code style
- Include tests for new functionality
- Ensure all tests pass before submitting
EOF
```

### Full Solution

Create a `CONTRIBUTING.md` in the repository root with setup instructions, coding standards, and PR guidelines tailored to the .NET stack.

## Acceptance Criteria

- [ ] CONTRIBUTING.md file exists in the repository root

## References

- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
