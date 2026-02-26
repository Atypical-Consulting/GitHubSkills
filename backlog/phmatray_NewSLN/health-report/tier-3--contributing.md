# CONTRIBUTING.md

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No CONTRIBUTING.md file exists in the repository.

## Why It Matters

Without contribution guidelines, new contributors don't know the expected workflow, coding standards, or how to set up their development environment. This creates friction and inconsistent contributions.

## How to Fix

### Quick Fix

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## Development Setup

```bash
dotnet restore
dotnet build
dotnet test
```

## Code Style

Follow the existing code conventions in the project.
EOF
git add CONTRIBUTING.md && git commit -m "Add contributing guidelines" && git push
```

### Full Solution

Add sections for: development environment setup, coding standards, commit message conventions, PR review process, and issue labeling.

## Acceptance Criteria

- [ ] CONTRIBUTING.md exists in the repository root

## References

- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
