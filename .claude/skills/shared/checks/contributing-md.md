---
name: Contributing Guidelines
slug: contributing-md
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Contributing Guidelines

## Verification

```bash
gh api repos/{owner}/{repo}/contents/CONTRIBUTING.md 2>&1 || true
```

### Pass Condition
The CONTRIBUTING.md file exists in the repository.

### Status Rules
- **PASS**: CONTRIBUTING.md exists in the repository root
- **FAIL**: CONTRIBUTING.md is missing from the repository

## Backlog Content

### What's Missing
No CONTRIBUTING.md file exists in the repository.

### Why It Matters
Without contribution guidelines, potential contributors don't know how to set up the project, what coding standards to follow, or how to submit changes. This raises the barrier to contribution and leads to inconsistent PRs.

### Quick Fix
```bash
# Create CONTRIBUTING.md in the repository root
touch CONTRIBUTING.md
```

### Full Solution
Generate a CONTRIBUTING.md tailored to the tech stack:

```markdown
# Contributing to {repo}

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. Fork and clone the repository
2. Install dependencies:
   {tech-stack-specific instructions}
3. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

{tech-stack-specific style guidance, e.g., "Run `dotnet format` before committing" or "Follow PEP 8 guidelines"}

## Making Changes

1. Make your changes in a feature branch
2. Write or update tests as needed
3. Ensure all tests pass:
   {tech-stack-specific test command}
4. Commit your changes with a clear message

## Pull Request Process

1. Update documentation if your changes affect it
2. Ensure CI passes on your PR
3. Request a review from the maintainers
4. Address any review feedback

## Reporting Issues

- Use the GitHub issue tracker
- Check existing issues before creating a new one
- Use the provided issue templates when available

## Code of Conduct

Please be respectful and constructive in all interactions.
```

### Acceptance Criteria
- [ ] CONTRIBUTING.md exists in the repository root

### Notes
Tailor setup instructions to the actual tech stack. Do not use generic placeholders. If the project has a code style enforcer (Prettier, ESLint, dotnet-format, Black), mention it.

### References
- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
