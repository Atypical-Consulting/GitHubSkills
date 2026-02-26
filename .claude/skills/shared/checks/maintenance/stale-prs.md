---
name: Stale PRs
slug: stale-prs
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Stale PRs

## Verification

```bash
echo "=== OPEN PRS ===" && (gh pr list --repo {owner}/{repo} --state open --json number,title,updatedAt,isDraft,author --jq '.[] | select((.updatedAt | fromdateiso8601) < (now - 2592000)) | "\(.number)\t\(.title)\t\(.updatedAt)\t\(.isDraft)\t\(.author.login)"' 2>&1 || true)
echo "=== TOTAL OPEN PRS ===" && (gh pr list --repo {owner}/{repo} --state open --json number --jq 'length' 2>&1 || true)
```

### Pass Condition
No open pull requests have gone without activity for more than 30 days.

### Status Rules
- **PASS**: Zero PRs are stale (all open PRs updated within the last 30 days), or no open PRs exist
- **FAIL**: One or more open PRs have not been updated in over 30 days
- **WARN**: PR listing returns 403 (insufficient permissions)

## Backlog Content

### What's Missing
One or more open pull requests have not been updated in over 30 days, indicating they may be forgotten or blocked.

### Why It Matters
Stale PRs represent unfinished work that's sitting in limbo — code that was written but never shipped. They confuse contributors about what's in progress, can accumulate merge conflicts over time, and make the project look poorly maintained. Addressing stale PRs (merge, close, or update) keeps the contribution pipeline healthy and signals an active project.

### Quick Fix
```bash
# List stale PRs to review
gh pr list --repo {owner}/{repo} --state open --json number,title,updatedAt \
  --jq '.[] | select((.updatedAt | fromdateiso8601) < (now - 2592000))'
```

### Full Solution
1. Review each stale PR and decide:
   - **Ready to merge**: Merge it (use `ghs-merge-prs` for batch operations)
   - **Needs work**: Leave a comment requesting updates, or push fixes yourself
   - **Abandoned**: Close with a comment explaining why
   - **Blocked**: Add a label like `blocked` and comment on what's needed
2. For bot PRs (Renovate, Dependabot):
   - If CI passes, merge them — dependency updates go stale fast
   - If CI fails, close and let the bot create a fresh PR with the latest versions
3. Consider setting up PR reminders:
   ```bash
   # GitHub scheduled reminders (via GitHub Settings > Scheduled Reminders)
   # Or use the gh CLI to review periodically
   gh pr list --repo {owner}/{repo} --state open --json number,title,updatedAt \
     --jq '[.[] | select((.updatedAt | fromdateiso8601) < (now - 604800))] | length'
   ```

### Acceptance Criteria
- [ ] No open PRs have been inactive for more than 30 days

### Notes
The 30-day threshold is more aggressive than the stale issues check (365 days) because PRs represent active code changes that become harder to merge over time. Bot PRs especially should be merged quickly or closed — dependency versions move fast.

### References
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests
- https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-membership-in-organizations/managing-your-scheduled-reminders
