---
name: Workflow Naming
slug: workflow-naming
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Workflow Naming

## Verification

```bash
# List workflow files
WORKFLOWS=$(gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name' 2>/dev/null || true)
if [ -z "$WORKFLOWS" ]; then
  echo "NO_WORKFLOWS"
  exit 0
fi
# Check each workflow for a top-level name: field
MISSING=""
for f in $WORKFLOWS; do
  CONTENT=$(gh api repos/{owner}/{repo}/contents/.github/workflows/$f --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || true)
  HAS_NAME=$(echo "$CONTENT" | grep -cE '^name:' || true)
  if [ "$HAS_NAME" -eq 0 ]; then
    MISSING="$MISSING $f"
  fi
done
if [ -z "$MISSING" ]; then
  echo "ALL_NAMED"
else
  echo "MISSING_NAME:$MISSING"
fi
```

### Pass Condition
Every workflow file has a top-level `name:` field, giving it a human-readable name in the GitHub Actions UI.

### Status Rules
- **PASS**: All workflow files contain a top-level `name:` field
- **FAIL**: At least one workflow file is missing a top-level `name:` field
- **INFO**: No workflow files exist (the separate `ci-cd-workflows` check covers existence)

## Backlog Content

### What's Missing
One or more GitHub Actions workflow files do not have a top-level `name:` field. Without it, GitHub displays the file name (e.g., `ci.yml`) instead of a descriptive name in the Actions tab.

### Why It Matters
Workflow names appear in the GitHub Actions UI, status checks, PR check lists, and badge URLs. Without a `name:` field, the display defaults to the filename, which is less readable and harder to distinguish when a repo has multiple workflows.

### Quick Fix
```yaml
# Add at the very top of the workflow file
name: CI
```

### Full Solution
1. List all workflow files: `gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name'`
2. For each file missing `name:`, add a descriptive name at the top of the file:
   - Use concise, descriptive names: `CI`, `Deploy`, `Release`, `Lint`, `CodeQL Analysis`
   - Place `name:` as the first line in the file (before `on:`)
3. Verify the workflow file is still valid YAML after the change

### Acceptance Criteria
- [ ] Every workflow file has a top-level `name:` field
- [ ] Names are descriptive and concise
- [ ] Workflow files remain valid YAML after changes

### References
- https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#name
