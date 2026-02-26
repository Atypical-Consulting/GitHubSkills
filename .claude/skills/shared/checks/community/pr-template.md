---
name: PR Template
slug: pr-template
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# PR Template

## Verification

```bash
echo "=== LOWER ===" && (gh api repos/{owner}/{repo}/contents/.github/pull_request_template.md 2>&1 || true)
echo "=== UPPER ===" && (gh api repos/{owner}/{repo}/contents/.github/PULL_REQUEST_TEMPLATE.md 2>&1 || true)
echo "=== DIR ===" && (gh api repos/{owner}/{repo}/contents/.github/PULL_REQUEST_TEMPLATE 2>&1 || true)
```

### Pass Condition
A pull request template exists in any of the standard locations.

### Status Rules
- **PASS**: Template exists in any standard location
- **FAIL**: Template is missing from all locations

## Backlog Content

### What's Missing
No pull request template is configured for the repository.

### Why It Matters
Without a PR template, pull requests arrive with inconsistent descriptions. Templates ensure every PR includes a summary, related issue link, and a checklist — making reviews faster and more thorough.

### Quick Fix
```bash
mkdir -p .github
# Create .github/pull_request_template.md
```

### Full Solution
Create `.github/pull_request_template.md`:

```markdown
## Summary
Brief description of what this PR does.

## Related Issue
Fixes #(issue number)

## Changes
- Change one
- Change two

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have added tests that prove my fix or feature works
- [ ] New and existing tests pass locally
- [ ] I have updated the documentation accordingly
```

### Acceptance Criteria
- [ ] PR template exists in one of the standard locations

### Notes
GitHub is case-insensitive for the filename. Lowercase `.github/pull_request_template.md` is the most common convention. Adapt checklist items to the project's requirements.

### References
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
