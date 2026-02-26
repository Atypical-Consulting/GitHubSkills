---
name: Stale Issues
slug: stale-issues
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Stale Issues

## Verification

```bash
echo "=== OPEN ISSUES ===" && (gh issue list --repo {owner}/{repo} --state open --json number,title,updatedAt --jq '.[] | select((.updatedAt | fromdateiso8601) < (now - 31536000)) | "\(.number)\t\(.title)\t\(.updatedAt)"' 2>&1 || true)
echo "=== TOTAL OPEN ===" && (gh issue list --repo {owner}/{repo} --state open --json number --jq 'length' 2>&1 || true)
```

### Pass Condition
No open issues have gone without activity for more than 365 days.

### Status Rules
- **PASS**: Zero issues are stale (all open issues updated within the last 365 days), or no open issues exist
- **FAIL**: One or more open issues have not been updated in over 365 days
- **WARN**: Issue listing returns 403 (insufficient permissions)

## Backlog Content

### What's Missing
One or more open issues have not been updated in over a year, signaling potential maintenance neglect.

### Why It Matters
Stale issues create noise for contributors, make the project look unmaintained, and hide real priorities. A backlog full of year-old untouched issues discourages new contributors and makes it harder to assess what actually needs attention.

### Quick Fix
```bash
# List stale issues to review
gh issue list --repo {owner}/{repo} --state open --json number,title,updatedAt \
  --jq '.[] | select((.updatedAt | fromdateiso8601) < (now - 31536000))'
```

### Full Solution
1. Review each stale issue and decide:
   - **Still relevant**: Add a comment with current status, update labels
   - **Won't fix**: Close with an explanation
   - **Duplicate**: Close and reference the duplicate
2. Consider adding a stale bot to automate future cleanup:
   ```yaml
   # .github/workflows/stale.yml
   name: Close stale issues
   on:
     schedule:
       - cron: '0 0 * * 1'
   jobs:
     stale:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/stale@v9
           with:
             stale-issue-message: 'This issue has been inactive for 60 days. It will be closed in 14 days if no further activity occurs.'
             days-before-stale: 60
             days-before-close: 14
   ```

### Acceptance Criteria
- [ ] No open issues have been inactive for more than 365 days

### Notes
The 365-day threshold is intentionally generous — it flags only severely neglected issues. The stale bot workflow is optional and uses a more aggressive 60-day cycle for ongoing maintenance.

### References
- https://github.com/actions/stale
