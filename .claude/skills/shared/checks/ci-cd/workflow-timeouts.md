---
name: Workflow Timeouts
slug: workflow-timeouts
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Workflow Timeouts

## Verification

```bash
# List workflow files
WORKFLOWS=$(gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name' 2>/dev/null || true)
if [ -z "$WORKFLOWS" ]; then
  echo "NO_WORKFLOWS"
  exit 0
fi
# Check each workflow — every job should have timeout-minutes
MISSING=""
for f in $WORKFLOWS; do
  CONTENT=$(gh api repos/{owner}/{repo}/contents/.github/workflows/$f --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || true)
  # Count jobs and timeout declarations
  JOB_COUNT=$(echo "$CONTENT" | grep -cE '^\s{2,4}\w[\w-]*:$' || true)
  TIMEOUT_COUNT=$(echo "$CONTENT" | grep -cE 'timeout-minutes:' || true)
  if [ "$JOB_COUNT" -gt 0 ] && [ "$TIMEOUT_COUNT" -lt "$JOB_COUNT" ]; then
    MISSING="$MISSING $f"
  fi
done
if [ -z "$MISSING" ]; then
  echo "ALL_HAVE_TIMEOUTS"
else
  echo "MISSING_TIMEOUTS:$MISSING"
fi
```

### Pass Condition
Every job in every workflow file declares a `timeout-minutes` value, preventing hung runners from consuming minutes indefinitely.

### Status Rules
- **PASS**: All jobs across all workflow files have `timeout-minutes` set
- **FAIL**: At least one job in at least one workflow file is missing `timeout-minutes`
- **INFO**: No workflow files exist (the separate `ci-cd-workflows` check covers existence)

## Backlog Content

### What's Missing
One or more jobs in GitHub Actions workflows do not declare `timeout-minutes`. The default timeout is 6 hours (360 minutes), meaning a hung runner can silently consume CI minutes.

### Why It Matters
Without explicit timeouts, a stuck build or test can run for up to 6 hours before GitHub cancels it. This wastes CI minutes (especially on paid plans), delays feedback, and can block other queued workflows. Setting reasonable timeouts ensures fast failure detection.

### Quick Fix
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # Add this line
    steps:
      - uses: actions/checkout@v4
```

### Full Solution
1. List all workflow files: `gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name'`
2. For each workflow, identify jobs missing `timeout-minutes`
3. Add appropriate timeout values based on job type:
   - **Lint/format checks**: 5–10 minutes
   - **Unit tests**: 10–15 minutes
   - **Build/compile**: 15–30 minutes
   - **Integration tests**: 15–30 minutes
   - **Deploy**: 10–20 minutes
   - **CodeQL analysis**: 30–60 minutes
4. Place `timeout-minutes:` at the job level (not the step level)
5. Verify workflow files remain valid YAML

### Acceptance Criteria
- [ ] Every job in every workflow file has `timeout-minutes` set
- [ ] Timeout values are reasonable for the job type (not just a blanket 360)
- [ ] Workflow files remain valid YAML after changes

### References
- https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes
