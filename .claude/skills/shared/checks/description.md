---
name: Description
slug: description
tier: 1
tier_label: Required
points: 4
scoring: normal
---

# Description

## Verification

```bash
gh repo view {owner}/{repo} --json description -q '.description' 2>&1 || true
```

### Pass Condition

Non-empty string.

### Status Rules

- **PASS**: Description is non-empty
- **FAIL**: Description is empty or not set

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

The repository has no description set.

### Why It Matters

The description appears on the repository page, in search results, and in API responses. Without it, the repo lacks discoverability and context for visitors browsing GitHub.

### Quick Fix

```bash
gh repo edit {owner}/{repo} --description "Your project description here"
```

### Full Solution

Craft a meaningful one-line description by inspecting the repository:
- Read the README (if it exists) for a summary.
- Check package.json `description`, .csproj `<Description>`, Cargo.toml `description`, or pyproject.toml `description`.
- Look at the repo name and directory structure for clues.

The description should be concise (under 350 characters), informative, and avoid generic phrases like "A project" or "My repo".

### Acceptance Criteria

- [ ] Repository description is a non-empty string
- [ ] Description is meaningful and accurately reflects the project

### Notes

- This is an **API-only fix** -- no file changes or PR needed.
- The `gh repo edit` command updates the description immediately.

### References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
