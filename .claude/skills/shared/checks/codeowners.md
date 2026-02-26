---
name: CODEOWNERS
slug: codeowners
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# CODEOWNERS

## Verification

```bash
echo "=== ROOT ===" && (gh api repos/{owner}/{repo}/contents/CODEOWNERS 2>&1 || true)
echo "=== GITHUB ===" && (gh api repos/{owner}/{repo}/contents/.github/CODEOWNERS 2>&1 || true)
echo "=== DOCS ===" && (gh api repos/{owner}/{repo}/contents/docs/CODEOWNERS 2>&1 || true)
```

### Pass Condition
The `CODEOWNERS` file exists in any of the three standard locations.

### Status Rules
- **PASS**: File exists in root, `.github/`, or `docs/`
- **FAIL**: File is missing from all three locations

## Backlog Content

### What's Missing
No CODEOWNERS file exists in the repository.

### Why It Matters
CODEOWNERS automatically assigns reviewers when pull requests touch specific paths. Without it, PR reviews depend on manual assignment, which often means no one reviews or the wrong person does.

### Quick Fix
```bash
mkdir -p .github && echo "* @{owner}" > .github/CODEOWNERS
```

### Full Solution
A more granular file maps specific paths to owners:

```
# Default owner for everything
* @{owner}

# Examples (adapt to repo structure):
# /docs/    @{owner}
# /src/     @{owner}
# *.md      @{owner}
```

For solo repos, `* @{owner}` is sufficient. For team repos, map directories to team members.

### Acceptance Criteria
- [ ] `CODEOWNERS` file exists in one of the standard locations: root, `.github/`, or `docs/`

### Notes
GitHub checks in order: root, `docs/`, `.github/`. The `.github/` location is conventional. Invalid syntax causes GitHub to silently ignore the file.

### References
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
