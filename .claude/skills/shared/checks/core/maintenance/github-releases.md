---
name: GitHub Releases
slug: github-releases
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# GitHub Releases

## Verification

```bash
gh release list --repo {owner}/{repo} --limit 5 2>&1 || true
```

### Pass Condition
At least one GitHub release or tag exists in the repository.

### Status Rules
- **PASS**: At least 1 release exists
- **FAIL**: No releases found

## Backlog Content

### What's Missing
No GitHub releases exist in this repository despite active development.

### Why It Matters
Releases formalize version milestones and provide downloadable artifacts. Without them, users have no clear way to know which version is stable, what changed, or when to upgrade. Releases also enable downstream tooling (package managers, dependency bots) to track versions properly.

### Quick Fix
```bash
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release" --repo {owner}/{repo}
```

### Full Solution
1. Choose a versioning scheme (Semantic Versioning recommended):
   - `v1.0.0` for stable releases
   - `v0.x.x` for pre-1.0 development
2. Create the release:
   ```bash
   gh release create v0.1.0 \
     --title "v0.1.0" \
     --generate-notes \
     --repo {owner}/{repo}
   ```
3. For mature projects, consider automating releases via CI (e.g., release-please, semantic-release, or a manual workflow dispatch).

### Acceptance Criteria
- [ ] At least one GitHub release exists

### Notes
The `--generate-notes` flag auto-generates release notes from merged PRs and commits since the last release. If the project has a CHANGELOG.md, consider referencing it in release notes instead.

### References
- https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- https://semver.org/
