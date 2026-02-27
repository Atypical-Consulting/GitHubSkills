---
name: Discussions Enabled
slug: discussions-enabled
tier: 3
tier_label: Nice to Have
points: 0
scoring: info
---

# Discussions Enabled

## Verification

```bash
gh api repos/{owner}/{repo} --jq '.has_discussions' 2>&1 || true
```

### Pass Condition
GitHub Discussions feature is enabled on the repository.

### Status Rules
- **PASS**: `has_discussions` is `true`
- **INFO**: `has_discussions` is `false` (no penalty, no points deducted)

## Backlog Content

### What's Missing
GitHub Discussions is not enabled on this repository.

### Why It Matters
Discussions provide a dedicated space for Q&A, ideas, and announcements without cluttering the issue tracker. They reduce noise in issues by giving users a place for questions that aren't bugs or feature requests. For community-facing projects, they're a lightweight alternative to forums or chat.

### Quick Fix
Enable via GitHub UI: Settings → General → Features → check "Discussions".

Or via API:
```bash
gh api repos/{owner}/{repo} -X PATCH -f has_discussions=true
```

### Full Solution
1. Enable Discussions via the API:
   ```bash
   gh api repos/{owner}/{repo} -X PATCH -f has_discussions=true
   ```
2. Consider creating default discussion categories:
   - **Announcements**: For project updates (maintainers only)
   - **Q&A**: For user questions (enables "mark as answer")
   - **Ideas**: For feature brainstorming
   - **Show and Tell**: For community showcases

### Acceptance Criteria
- [ ] GitHub Discussions feature is enabled

### Notes
This is an **INFO-only check**. It carries no points and no penalty. Discussions are most valuable for public, community-facing projects. For private repos or solo projects, this feature may not be needed. Only suggest enabling it if the project has community engagement or the user expresses interest.

### References
- https://docs.github.com/en/discussions/quickstart
