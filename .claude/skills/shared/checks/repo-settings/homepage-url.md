---
name: Homepage URL
slug: homepage-url
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Homepage URL

## Verification

```bash
gh api repos/{owner}/{repo} --jq '.homepage // empty' 2>&1 || true
```

### Pass Condition
The repository has a non-empty homepage URL set.

### Status Rules
- **PASS**: Homepage URL is set and non-empty
- **FAIL**: Homepage URL is empty or null

## Backlog Content

### What's Missing
No homepage URL is set on the repository.

### Why It Matters
The homepage URL appears prominently on the repository page and directs users to documentation, a live demo, or the project website. Without it, users must search through the README or guess where to find more information.

### Quick Fix
```bash
gh repo edit {owner}/{repo} --homepage "https://example.com"
```

### Full Solution
Set the homepage to the most useful link for users:

- **Documentation site**: If the project has hosted docs (GitHub Pages, ReadTheDocs, etc.)
- **Live demo**: If there's a deployed instance users can try
- **NuGet/npm/PyPI page**: If it's a published package
- **Project website**: If there's a dedicated site

```bash
gh repo edit {owner}/{repo} --homepage "https://your-project-url.com"
```

### Acceptance Criteria
- [ ] Repository has a non-empty homepage URL

### Notes
This is an **API-only fix** — no file changes or PR needed. If the project doesn't have a website or docs site, consider enabling GitHub Pages for the repo's README or docs directory.

### References
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-repository-languages#changing-the-homepage-url
