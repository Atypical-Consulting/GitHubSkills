# Branch Protection

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 1 — Required |
| **Points** | 4 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

The default branch `WIP-feature-backup-20260218` has no branch protection rules enabled.

## Why It Matters

Without branch protection, anyone with write access can push directly to the default branch, force-push over history, or merge without review. This increases the risk of accidental or unreviewed changes reaching production. Note: the default branch name `WIP-feature-backup-20260218` is unusual — consider renaming it to `main`.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/NewSLN/branches/WIP-feature-backup-20260218/protection -X PUT --input - <<'EOF'
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "enforce_admins": true,
  "required_status_checks": null,
  "restrictions": null
}
EOF
```

### Full Solution

1. Consider renaming the default branch to `main`:
   ```bash
   gh api repos/phmatray/NewSLN -X PATCH -f default_branch=main
   ```
2. Then apply branch protection on the new default branch with required reviews, status checks, and admin enforcement.

## Acceptance Criteria

- [ ] Branch protection API returns 200 for the default branch
- [ ] Required pull request reviews are enabled

## References

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-a-branch-protection-rule/about-protected-branches
