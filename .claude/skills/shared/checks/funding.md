---
name: Funding
slug: funding
tier: 3
tier_label: Nice to Have
points: 0
scoring: info
---

# Funding

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.github/FUNDING.yml 2>&1 || true
```

### Pass Condition
The FUNDING.yml file exists in the `.github/` directory.

### Status Rules
- **PASS**: File exists
- **INFO**: File missing (no penalty, no points deducted)

## Backlog Content

### What's Missing
No FUNDING.yml file exists.

### Why It Matters
The FUNDING.yml file adds a "Sponsor" button to the repository page, making it easy for users to support the project financially. It's entirely optional but can help sustain open-source work.

### Quick Fix
```yaml
# .github/FUNDING.yml
github: [{owner}]
```

### Full Solution
```yaml
github: [{owner}]
# patreon: username
# open_collective: project-name
# ko_fi: username
# custom: ["https://your-link.com"]
```

### Acceptance Criteria
- [ ] `.github/FUNDING.yml` exists

### Notes
This is an INFO-only check. It carries no points and no penalty. The funding file is purely optional and informational. Only suggest it if the user expresses interest in sponsorship. Do not auto-create during batch fixes unless explicitly asked.

### References
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository
