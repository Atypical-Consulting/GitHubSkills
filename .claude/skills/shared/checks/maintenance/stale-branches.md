---
name: Stale Branches
slug: stale-branches
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Stale Branches

## Verification

```bash
echo "=== DEFAULT BRANCH ===" && (gh repo view {owner}/{repo} --json defaultBranchRef --jq '.defaultBranchRef.name' 2>&1 || true)
echo "=== STALE BRANCHES ===" && (gh api repos/{owner}/{repo}/branches --paginate --jq '.[] | select(.name != "{default_branch}") | .name' 2>&1 | while read branch; do
  last_date=$(gh api "repos/{owner}/{repo}/commits?sha=$branch&per_page=1" --jq '.[0].commit.committer.date' 2>/dev/null || true)
  if [ -n "$last_date" ]; then
    last_epoch=$(date -d "$last_date" +%s 2>/dev/null || date -jf "%Y-%m-%dT%H:%M:%SZ" "$last_date" +%s 2>/dev/null || echo "0")
    now_epoch=$(date +%s)
    age_days=$(( (now_epoch - last_epoch) / 86400 ))
    if [ "$age_days" -gt 90 ]; then
      echo "$branch	$age_days days	$last_date"
    fi
  fi
done)
```

### Pass Condition
No non-default branches have gone without commits for more than 90 days.

### Status Rules
- **PASS**: Zero stale branches (all non-default branches have commits within the last 90 days), or only the default branch exists
- **FAIL**: One or more branches have not received commits in over 90 days
- **WARN**: Branch listing returns 403 (insufficient permissions)

## Backlog Content

### What's Missing
One or more branches have not received any commits in over 90 days and may be abandoned.

### Why It Matters
Stale branches clutter the repository, create confusion about what's actively being worked on, and can cause merge conflicts to accumulate. They also make branch listings harder to navigate and signal a lack of maintenance to contributors. Cleaning up stale branches keeps the repo tidy and makes it clear what work is in progress.

### Quick Fix
```bash
# List branches with their last commit date
gh api repos/{owner}/{repo}/branches --paginate --jq '.[].name' | while read branch; do
  date=$(gh api "repos/{owner}/{repo}/commits?sha=$branch&per_page=1" --jq '.[0].commit.committer.date' 2>/dev/null)
  echo "$branch  $date"
done
```

### Full Solution
1. Review each stale branch and decide:
   - **Has an open PR**: The PR should be merged or closed first, then the branch will be cleaned up
   - **Work abandoned**: Delete the branch (`git push origin --delete <branch>`)
   - **Still needed**: Push a commit or rebase to refresh it
2. Enable "Delete branch on merge" in repo settings to prevent stale branches from merged PRs
3. Consider periodic cleanup — review branches quarterly

### Acceptance Criteria
- [ ] No non-default branches have been inactive for more than 90 days

### Notes
The 90-day threshold catches branches that are likely abandoned while giving enough runway for longer-running feature branches. Branches associated with open PRs are still flagged — the PR itself should be addressed.

### References
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/deleting-and-restoring-branches-in-a-repository
