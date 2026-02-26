---
name: New Health Check
about: Propose a new health check for ghs-repo-scan
title: "[CHECK] "
labels: new-check
assignees: ""
---

## Check Name

A short, human-readable name for this check (e.g., "EditorConfig present").

## Slug

The kebab-case identifier for this check (e.g., `editorconfig-present`).

## Category

<!-- Choose one: -->
- [ ] documentation
- [ ] repo-settings
- [ ] dev-config
- [ ] ci-cd
- [ ] community
- [ ] security
- [ ] maintenance

## Suggested Tier

<!-- Choose one: -->
- [ ] Tier 1 (critical, high impact)
- [ ] Tier 2 (recommended, moderate impact)
- [ ] Tier 3 (nice-to-have, low impact)

## Verification Command

How should ghs-repo-scan determine PASS or FAIL? Describe the command or file check.

```bash
# Example: test -f .editorconfig && echo PASS || echo FAIL
```

## Backlog Content

What should be written to the backlog item if this check fails? Include a brief description and remediation steps.

## Why this check matters

Explain the value this check provides to repository maintainers.
