---
name: Changelog
slug: changelog
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Changelog

## Verification

```bash
echo "=== CHANGELOG ===" && (gh api repos/{owner}/{repo}/contents/CHANGELOG.md 2>&1 || true)
echo "=== CHANGES ===" && (gh api repos/{owner}/{repo}/contents/CHANGES.md 2>&1 || true)
echo "=== HISTORY ===" && (gh api repos/{owner}/{repo}/contents/HISTORY.md 2>&1 || true)
```

### Pass Condition
A changelog file exists in the repository root under one of the standard names: CHANGELOG.md, CHANGES.md, or HISTORY.md.

### Status Rules
- **PASS**: At least one changelog file exists
- **FAIL**: No changelog file found

## Backlog Content

### What's Missing
No changelog file (CHANGELOG.md, CHANGES.md, or HISTORY.md) exists in the repository.

### Why It Matters
A changelog communicates what changed between versions to users and contributors. Without one, users must dig through commit logs to understand what's new, what's fixed, or what might break. It's a key signal of project maturity and maintainer discipline.

### Quick Fix
```bash
touch CHANGELOG.md
```

### Full Solution
Create a CHANGELOG.md following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial project setup
```

### Acceptance Criteria
- [ ] A changelog file exists in the repository root (CHANGELOG.md, CHANGES.md, or HISTORY.md)

### Notes
Prefer CHANGELOG.md as the filename — it's the most widely recognized convention. The Keep a Changelog format is recommended but not required.

### References
- https://keepachangelog.com/
- https://common-changelog.org/
