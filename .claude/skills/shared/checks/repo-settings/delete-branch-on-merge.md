---
name: Delete Branch on Merge
slug: delete-branch-on-merge
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Delete Branch on Merge

## Verification

```bash
gh api repos/{owner}/{repo} --jq '.delete_branch_on_merge' 2>&1 || true
```

### Pass Condition
The repository setting `delete_branch_on_merge` is `true`, so head branches are automatically deleted after pull requests are merged.

### Status Rules
- **PASS**: `delete_branch_on_merge` is `true`
- **FAIL**: `delete_branch_on_merge` is `false`

## Backlog Content

### What's Missing
Automatic branch deletion after merge is not enabled. Merged branches accumulate over time, cluttering the branch list and making it harder to find active work.

### Why It Matters
Without auto-delete, merged feature branches pile up. This creates noise in the branch list, makes it harder to find active branches, and can confuse contributors about what's current. It's a one-click setting that prevents ongoing cleanup work.

### Quick Fix
```bash
gh api repos/{owner}/{repo} -X PATCH -f delete_branch_on_merge=true
```

### Full Solution
Enable the setting via the API:

```bash
gh api repos/{owner}/{repo} -X PATCH -f delete_branch_on_merge=true
```

Or via GitHub UI: Settings → General → Pull Requests → check "Automatically delete head branches".

### Acceptance Criteria
- [ ] `delete_branch_on_merge` is `true`

### Notes
This is an **API-only fix** — no file changes or PR needed. It only affects future merges; existing stale branches must be cleaned up separately.

### References
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches
