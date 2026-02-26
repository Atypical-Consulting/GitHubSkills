---
name: Issue Templates
slug: issue-templates
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Issue Templates

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE 2>&1 || true
```

### Pass Condition
The `.github/ISSUE_TEMPLATE/` directory exists and contains at least one file.

### Status Rules
- **PASS**: Directory exists with >= 1 file
- **FAIL**: Directory is missing or empty

## Backlog Content

### What's Missing
No issue templates are configured for the repository.

### Why It Matters
Without templates, bug reports and feature requests arrive in inconsistent formats, missing crucial details like reproduction steps or environment info. Templates guide contributors to provide the information maintainers need.

### Quick Fix
```bash
mkdir -p .github/ISSUE_TEMPLATE
```

### Full Solution
Create two starter templates:

`.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug Report
about: Report a bug to help us improve
title: '[Bug] '
labels: bug
assignees: ''
---

## Description
A clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Windows 11, macOS 14]
- Version: [e.g., 1.0.0]

## Additional Context
Any other context, screenshots, or logs.
```

`.github/ISSUE_TEMPLATE/feature_request.md`:
```markdown
---
name: Feature Request
about: Suggest an idea for this project
title: '[Feature] '
labels: enhancement
assignees: ''
---

## Problem
A clear description of the problem this feature would solve.

## Proposed Solution
Your idea for how to solve it.

## Alternatives Considered
Any alternative solutions or features you've considered.

## Additional Context
Any other context, mockups, or examples.
```

### Acceptance Criteria
- [ ] `.github/ISSUE_TEMPLATE/` directory exists with at least one template file

### Notes
You can add a `config.yml` to add blank issue options or external links. Template names and labels should match existing conventions.

### References
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
