---
name: Workflow Concurrency
slug: workflow-concurrency
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Workflow Concurrency

## Verification

```bash
# List workflow files
WORKFLOWS=$(gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name' 2>/dev/null || true)
if [ -z "$WORKFLOWS" ]; then
  echo "NO_WORKFLOWS"
  exit 0
fi
# Check workflows triggered by pull_request for concurrency groups
MISSING=""
for f in $WORKFLOWS; do
  CONTENT=$(gh api repos/{owner}/{repo}/contents/.github/workflows/$f --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || true)
  IS_PR_TRIGGERED=$(echo "$CONTENT" | grep -cE '^\s*(pull_request|pull_request_target):' || true)
  HAS_CONCURRENCY=$(echo "$CONTENT" | grep -cE '^concurrency:' || true)
  if [ "$IS_PR_TRIGGERED" -gt 0 ] && [ "$HAS_CONCURRENCY" -eq 0 ]; then
    MISSING="$MISSING $f"
  fi
done
if [ -z "$MISSING" ]; then
  echo "ALL_HAVE_CONCURRENCY"
else
  echo "MISSING_CONCURRENCY:$MISSING"
fi
```

### Pass Condition
Every workflow file triggered by `pull_request` or `pull_request_target` declares a top-level `concurrency:` group, ensuring redundant runs are cancelled when new commits are pushed to the same PR.

### Status Rules
- **PASS**: All PR-triggered workflows have a `concurrency:` block
- **FAIL**: At least one PR-triggered workflow is missing a `concurrency:` block
- **INFO**: No workflow files exist, or no workflows are PR-triggered

## Backlog Content

### What's Missing
One or more PR-triggered workflows do not use `concurrency:` groups. When a developer pushes multiple commits to a PR in quick succession, each push triggers a new workflow run — all running in parallel and wasting CI minutes.

### Why It Matters
Without concurrency groups, pushing 5 quick commits to a PR creates 5 parallel CI runs, but only the last one matters. This wastes CI minutes, clogs the runner queue, and slows down feedback for the entire team. Concurrency groups with `cancel-in-progress: true` automatically cancel stale runs.

### Quick Fix
```yaml
# Add at the top level of PR-triggered workflows (after permissions:)
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Full Solution
1. List all workflow files: `gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name'`
2. Identify workflows triggered by `pull_request` or `pull_request_target`
3. For each, add a `concurrency:` block at the top level:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```
4. For deploy workflows on `main`, use `cancel-in-progress: false` to avoid cancelling active deployments:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
   ```
5. Verify workflow files remain valid YAML

### Acceptance Criteria
- [ ] All PR-triggered workflows have a top-level `concurrency:` block
- [ ] Concurrency groups use `${{ github.workflow }}-${{ github.ref }}` or equivalent
- [ ] `cancel-in-progress: true` is set for PR workflows
- [ ] Workflow files remain valid YAML after changes

### References
- https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
