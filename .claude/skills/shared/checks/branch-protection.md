---
name: Branch Protection
slug: branch-protection
tier: 1
tier_label: Required
points: 4
scoring: normal
---

# Branch Protection

## Verification

```bash
gh api repos/{owner}/{repo}/branches/{default_branch}/protection 2>&1 || true
```

### Pass Condition

Returns 200 (not 404). If 403, report as WARN (insufficient permissions).

### Status Rules

- **PASS**: API returns 200
- **FAIL**: API returns 404
- **WARN**: API returns 403 (requires admin access)

**Important -- Solo maintainer awareness**: Detect if the repo has a single owner/contributor (check collaborators count or org membership). For solo repos, branch protection is still recommended but the backlog item should suggest a lightweight config (no required reviews, just force-push protection and enforce admins) since requiring PR approvals blocks the sole maintainer from merging.

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

No branch protection rules are configured for the default branch.

### Why It Matters

Without branch protection, anyone with push access can force-push to the default branch, accidentally delete it, or push breaking changes without review. Even solo maintainers benefit from force-push protection as a safety net against accidental history rewrites.

### Quick Fix

```bash
gh api repos/{owner}/{repo}/branches/{default_branch}/protection \
  -X PUT \
  --input - <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### Full Solution

The configuration depends on whether the repo is solo-maintained or team-based.

**Solo maintainer repos** (single collaborator, or `owner.type` is `User` with no additional collaborators):
```json
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```
Key point: `required_pull_request_reviews` is `null` -- requiring PR approvals would lock the sole maintainer out.

**Team repos** (2+ collaborators, or org-owned):
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```
If CI/CD workflows exist, populate `contexts` with detected status check names.

### Acceptance Criteria

- [ ] Branch protection API returns 200 for the default branch
- [ ] Force pushes are blocked
- [ ] Admins are included in enforcement

### Notes

- This is an **API-only fix** -- no file changes or PR needed.
- Requires admin access to the repository. If the user is not an admin, the API will return 403.
- If the default branch name is unusual (e.g., `develop`), consider noting that renaming to `main` is a common best practice.

### References

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-a-branch-protection-rule/about-protected-branches
