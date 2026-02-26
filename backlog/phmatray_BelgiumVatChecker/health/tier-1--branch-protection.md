# Branch Protection

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 1 — Required |
| **Points** | 4 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

The default branch `main` has no branch protection rules configured.

## Why It Matters

Without branch protection, anyone with write access can force-push to `main`, overwrite history, or push broken code directly. Even with only 2 contributors, branch protection prevents accidental force-pushes and ensures CI checks pass before merging.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/BelgiumVatChecker/branches/main/protection -X PUT --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### Full Solution

This repo has 2 contributors, so a lightweight config works well — no required PR reviews (which would block solo merges), but force-push protection and admin enforcement are enabled. If you later add more collaborators, consider enabling `required_pull_request_reviews` with at least 1 approver.

You can also configure this via the GitHub UI: Settings > Branches > Add branch protection rule for `main`.

## Acceptance Criteria

- [ ] Branch protection API returns 200 for the `main` branch
- [ ] Force pushes to `main` are blocked

## References

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-a-branch-protection-rule/managing-a-branch-protection-rule
