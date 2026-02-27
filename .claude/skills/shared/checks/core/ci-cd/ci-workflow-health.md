---
name: CI Workflow Health
slug: ci-workflow-health
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# CI Workflow Health

## Verification

```bash
gh run list --repo {owner}/{repo} --limit 10 --json conclusion,workflowName,status 2>&1 || true
```

### Pass Condition
No workflow has its most recent completed run in `failure` state. If all recent runs succeed or are `skipped`/`cancelled`, pass. If no workflows exist at all, mark as `[INFO]` (the separate CI/CD check covers existence).

### Status Rules
- **PASS**: All workflows have their most recent completed run with `success` or `skipped` conclusion
- **FAIL**: At least one workflow has its most recent completed run in `failure` state

## Backlog Content

### What's Missing
One or more GitHub Actions workflows have failing runs.

### Why It Matters
Failing CI pipelines indicate the project may have broken builds, failing tests, or outdated dependencies. This erodes confidence in the codebase and makes it harder for contributors to verify their changes work.

### Quick Fix
```bash
gh run list --repo {owner}/{repo} --status failure --limit 5
gh run view {run-id} --repo {owner}/{repo} --log-failed
```

### Full Solution
1. Identify which workflows are failing by checking the most recent run per workflow:
   `gh run list --repo {owner}/{repo} --limit 20 --json conclusion,workflowName,status,databaseId`
2. For each failing workflow, view the failed logs: `gh run view {run-id} --repo {owner}/{repo} --log-failed`
3. Common causes:
   - **Outdated dependencies**: lock file out of sync, removed packages
   - **Broken tests**: flaky tests, missing test fixtures, environment differences
   - **Deprecated actions**: using `actions/checkout@v2` when `v4` is available
   - **Expired secrets/tokens**: API keys or tokens that need rotation
   - **Platform changes**: runtime version no longer available (e.g., Node 16 EOL)
4. Fix the root cause and push to trigger a re-run.

### Acceptance Criteria
- [ ] All workflows have their most recent completed run with `success` or `skipped` conclusion
- [ ] No workflow has its latest completed run in `failure` state

### Notes
This check looks at the most recent completed run per workflow, not all historical runs. If a workflow is intentionally broken or unused, consider deleting or disabling it.

### References
- https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/monitoring-workflows/using-workflow-run-logs
