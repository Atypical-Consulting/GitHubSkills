---
name: Commit Signoff
slug: commit-signoff
tier: 3
tier_label: Nice to Have
points: 0
scoring: info
---

# Commit Signoff

## Verification

```bash
gh api repos/{owner}/{repo} --jq '.web_commit_signoff_required' 2>&1 || true
```

### Pass Condition
The repository requires web-based commit signoff (DCO — Developer Certificate of Origin).

### Status Rules
- **PASS**: `web_commit_signoff_required` is `true`
- **INFO**: `web_commit_signoff_required` is `false` (no penalty, no points deducted)

## Backlog Content

### What's Missing
Web commit signoff is not required for this repository.

### Why It Matters
The Developer Certificate of Origin (DCO) is a lightweight way to certify that contributors have the right to submit their code. Requiring signoff adds a `Signed-off-by` line to commits, providing a paper trail for IP compliance. It's used by the Linux kernel, CNCF projects, and many enterprise open-source projects.

### Quick Fix
```bash
gh api repos/{owner}/{repo} -X PATCH -f web_commit_signoff_required=true
```

### Full Solution
1. Enable web commit signoff:
   ```bash
   gh api repos/{owner}/{repo} -X PATCH -f web_commit_signoff_required=true
   ```
2. For local development, contributors add signoff with:
   ```bash
   git commit -s -m "Your commit message"
   ```
   Or configure it globally:
   ```bash
   git config --global commit.gpgsign true
   ```

### Acceptance Criteria
- [ ] `web_commit_signoff_required` is `true`

### Notes
This is an **INFO-only check**. It carries no points and no penalty. DCO signoff is primarily valuable for open-source projects with external contributors, enterprise compliance requirements, or projects under CNCF/Linux Foundation governance. For personal or small-team projects, it adds friction without much benefit. Only suggest enabling it if the project context warrants it.

### References
- https://developercertificate.org/
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-the-commit-signoff-policy-for-your-repository
